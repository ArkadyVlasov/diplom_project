from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Product, Category, Shop
from .serializers import ProductSerializer, CategorySerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().prefetch_related(
        'product_infos__shop', 
        'product_infos__parameters__parameter'
    )
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'product_infos__shop']
    search_fields = ['name']
    ordering_fields = ['name', 'product_infos__price']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all().prefetch_related(
        'product_infos__shop',
        'product_infos__parameters__parameter'
    )
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]