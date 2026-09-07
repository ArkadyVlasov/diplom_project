from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from shop.models import ProductInfo
from contacts.models import Contact          # импорт модели контакта
from .tasks import send_order_confirmation, send_order_notification_to_admin


class OrderListCreateView(generics.ListCreateAPIView):
    """
    Просмотр списка заказов пользователя и создание заказа (без обработки корзины).
    Обычно используется для админских нужд.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderConfirmView(views.APIView):
    """
    Подтверждение заказа:
    - Создаёт заказ из товаров в корзине пользователя,
    - Списывает остатки,
    - Привязывает контакт доставки,
    - Очищает корзину,
    - Отправляет письма через Celery.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем ID контакта из запроса
        contact_id = request.data.get('contact')
        if not contact_id:
            return Response(
                {"error": "Не указан ID контакта"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            contact = Contact.objects.get(id=contact_id, user=user)
        except Contact.DoesNotExist:
            return Response(
                {"error": "Контакт не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Создаём заказ со статусом 'new' и привязываем контакт
        order = Order.objects.create(
            user=user,
            status='new',
            contact=contact
        )

        total = 0
        for cart_item in cart_items:
            product_info = cart_item.product_info
            if product_info.quantity < cart_item.quantity:
                # Откат транзакции при нехватке товара
                raise ValueError(f"Недостаточно товара {product_info.product.name}")

            # Создаём позицию заказа
            OrderItem.objects.create(
                order=order,
                product_info=product_info,
                quantity=cart_item.quantity,
                price=product_info.price
            )
            # Уменьшаем остаток
            product_info.quantity -= cart_item.quantity
            product_info.save()
            total += product_info.price * cart_item.quantity

        order.total = total
        order.save()

        # Очищаем корзину
        cart_items.delete()

        # Асинхронная отправка писем через Celery
        send_order_confirmation.delay(order.id)
        send_order_notification_to_admin.delay(order.id)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    Обновление статуса заказа (доступно только для поставщиков или админов).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def perform_update(self, serializer):
        # Проверяем, что пользователь – поставщик или администратор
        if self.request.user.type != 'shop' and not self.request.user.is_staff:
            raise PermissionError("Только поставщики могут менять статус заказа")
        serializer.save()