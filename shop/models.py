from django.db import models
from django.conf import settings

class Shop(models.Model):
    """
    Магазин (поставщик). Связан с пользователем типа 'supplier'.
    """
    name = models.CharField(max_length=100, verbose_name='Название')
    url = models.URLField(blank=True, verbose_name='Ссылка')
    filename = models.CharField(max_length=100, blank=True, verbose_name='Имя файла импорта')
    is_active = models.BooleanField(default=True, verbose_name='Приём заказов')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop',
        verbose_name='Поставщик'
    )

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Категория товаров.
    """
    name = models.CharField(max_length=100, verbose_name='Название')
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True, verbose_name='Магазины')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Товар (абстрактная сущность, не привязанная к магазину).
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Информация о товаре конкретного магазина: цена, количество, внешний ID.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_infos', verbose_name='Товар')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos', verbose_name='Магазин')
    external_id = models.CharField(max_length=50, verbose_name='ID у поставщика')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Рекомендованная цена')

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Информация о товарах'
        unique_together = ('product', 'shop')

    def __str__(self):
        return f"{self.product.name} ({self.shop.name})"


class Parameter(models.Model):
    """
    Название характеристики (например, 'Цвет', 'Размер').
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='Название характеристики')

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Значение характеристики для конкретного ProductInfo.
    """
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='parameters', verbose_name='Товар в магазине')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters', verbose_name='Характеристика')
    value = models.CharField(max_length=100, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр товара'
        verbose_name_plural = 'Параметры товаров'
        unique_together = ('product_info', 'parameter')

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"