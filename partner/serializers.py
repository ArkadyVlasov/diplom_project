from rest_framework import serializers
from shop.models import Shop
from orders.models import Order, OrderItem
from contacts.serializers import ContactSerializer

class ShopStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'is_active']


class PartnerOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_info.product.name')
    shop_name = serializers.CharField(source='product_info.shop.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'shop_name', 'quantity', 'price']


class PartnerOrderSerializer(serializers.ModelSerializer):
    items = PartnerOrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'user_username', 'contact', 'total', 'items']