from django.db import models
from django.conf import settings
from shop.models import ProductInfo

class Order(models.Model):
    """
    Заказ пользователя.
    """
    STATUS_CHOICES = (
        ('basket', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтверждён'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменён'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='basket')
    address = models.TextField(blank=True, verbose_name='Адрес доставки')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Общая сумма')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ №{self.id} от {self.user.username}"


class OrderItem(models.Model):
    """
    Позиция заказа (фиксирует цену и количество на момент заказа).
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент заказа')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product_info.product.name} x{self.quantity} (заказ №{self.order.id})"