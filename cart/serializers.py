from rest_framework import serializers
from .models import Cart
from shop.serializers import ProductInfoSerializer

class CartSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'product_info', 'quantity', 'total_price')
    
    def get_total_price(self, obj):
        return obj.quantity * obj.product_info.price