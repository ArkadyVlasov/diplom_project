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