from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Расширенная модель пользователя.
    type: shop - поставщик, buyer - покупатель.
    is_active по умолчанию False – требуется подтверждение по email.
    """
    TYPE_CHOICES = (
        ('shop', 'Магазин (поставщик)'),
        ('buyer', 'Покупатель'),
    )
    company = models.CharField(max_length=100, blank=True, verbose_name='Компания')
    position = models.CharField(max_length=50, blank=True, verbose_name='Должность')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='buyer')
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_type_display()})"