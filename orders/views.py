from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart

class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product_info__product',
            'items__product_info__shop'
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Проверяем, есть ли у пользователя корзина
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Создаём заказ
        order = Order.objects.create(
            user=request.user,
            address=request.data.get('address', ''),
            status='new'
        )
        
        # Создаём позиции заказа
        total = 0
        for cart_item in cart_items:
            product_info = cart_item.product_info
            # Проверяем наличие товара
            if product_info.quantity < cart_item.quantity:
                return Response(
                    {'error': f'Not enough {product_info.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Уменьшаем количество на складе
            product_info.quantity -= cart_item.quantity
            product_info.save()
            
            # Создаём позицию заказа
            order_item = OrderItem.objects.create(
                order=order,
                product_info=product_info,
                quantity=cart_item.quantity,
                price=product_info.price
            )
            total += cart_item.quantity * product_info.price
        
        # Обновляем общую сумму заказа
        order.total = total
        order.save()
        
        # Очищаем корзину
        cart_items.delete()
        
        # Отправляем email (пока заглушка)
        # send_order_confirmation(order)  # позже реализуем
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product_info__product',
            'items__product_info__shop'
        )
        
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from shop.models import ProductInfo

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
    отправляет письма.
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
            address=request.data.get('address', '')  # ожидаем адрес в запросе
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

        # Отправка email клиенту (подтверждение заказа)
        self._send_order_confirmation(order)

        # Отправка email администратору (накладная)
        self._send_order_notification_to_admin(order)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    def _send_order_confirmation(self, order):
        subject = f'Подтверждение заказа №{order.id}'
        message = f'Ваш заказ №{order.id} на сумму {order.total} руб. принят.\nСпасибо за покупку!'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
        )

    def _send_order_notification_to_admin(self, order):
        subject = f'Новый заказ №{order.id}'
        message = f'Поступил новый заказ №{order.id} от {order.user.username}\nСумма: {order.total}\nАдрес: {order.address}'
        # Здесь можно указать email администратора (можно взять из настроек или из модели)
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [admin_email],
            fail_silently=False,
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