from django.db import models
from django.conf import settings
from shop.models import ProductInfo

class Cart(models.Model):
    """
    Корзина пользователя. Хранит товары, добавленные для заказа.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Корзина'
        unique_together = ('user', 'product_info')

    def __str__(self):
        return f"{self.user.username} - {self.product_info.product.name}"