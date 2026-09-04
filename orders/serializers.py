from rest_framework import serializers
from .models import Order, OrderItem
from shop.serializers import ProductInfoSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)
    product_name = serializers.CharField(source='product_info.product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'product_name', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'created_at', 'status', 'address', 'total', 'items')