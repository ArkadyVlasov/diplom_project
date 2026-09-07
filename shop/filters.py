import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    """
    Фильтр для товаров:
    - по категории (category)
    - по магазину (product_infos__shop)
    - по минимальной цене (price_min)
    - по максимальной цене (price_max)
    """
    price_min = django_filters.NumberFilter(
        field_name='product_infos__price',
        lookup_expr='gte',
        label='Цена от'
    )
    price_max = django_filters.NumberFilter(
        field_name='product_infos__price',
        lookup_expr='lte',
        label='Цена до'
    )

    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'product_infos__shop': ['exact'],
        }