from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from shop.models import ProductInfo
from .tasks import send_order_confirmation, send_order_notification_to_admin  # импортируем задачи


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderConfirmView(views.APIView):
    """
    Подтверждение заказа: создаёт заказ из корзины, списывает товары,
    отправляет письма через Celery.
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

        # Создаём заказ со статусом 'new'
        order = Order.objects.create(
            user=user,
            status='new',
            address=request.data.get('address', '')
        )

        total = 0
        for cart_item in cart_items:
            product_info = cart_item.product_info
            # Проверяем остаток
            if product_info.quantity < cart_item.quantity:
                # Если не хватает, откатываем транзакцию
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
        # Проверяем, что текущий пользователь является поставщиком
        if self.request.user.user_type != 'supplier' and not self.request.user.is_staff:
            raise PermissionError("Только поставщики могут менять статус заказа")
        serializer.save()