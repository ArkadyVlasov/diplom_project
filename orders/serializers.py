from rest_framework import serializers
from .models import Order, OrderItem
from contacts.serializers import ContactSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_info.product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)   # добавляем вложенный контакт

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'contact', 'total', 'items']