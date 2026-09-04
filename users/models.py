from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Расширенная модель пользователя.
    Может быть клиентом или поставщиком.
    """
    USER_TYPES = (
        ('client', 'Клиент'),
        ('supplier', 'Поставщик'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"