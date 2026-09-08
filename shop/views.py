from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter   # импортируем фильтр

class ProductListView(generics.ListAPIView):
    """
    Список товаров с фильтрацией по категории, магазину и цене.
    Доступно без авторизации.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter   # подключаем фильтр
    
class ProductDetailView(generics.RetrieveAPIView):
    """
    Получение детальной информации о товаре по ID.
    Доступно без авторизации.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]