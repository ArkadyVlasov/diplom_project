from rest_framework import serializers
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

class ProductParameterSerializer(serializers.ModelSerializer):
    parameter_name = serializers.CharField(source='parameter.name')
    
    class Meta:
        model = ProductParameter
        fields = ('parameter_name', 'value')

class ProductInfoSerializer(serializers.ModelSerializer):
    parameters = ProductParameterSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.name')
    
    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'shop', 'shop_name', 'external_id', 
                  'quantity', 'price', 'price_rrc', 'parameters')

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    product_infos = ProductInfoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'category_name', 'product_infos')

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'products')