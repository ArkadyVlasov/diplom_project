from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User.
    Использует email как основной идентификатор (USERNAME_FIELD).
    """
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязательно должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    USER_TYPES = (
        ('client', 'Клиент'),
        ('shop', 'Поставщик'),
    )
    type = models.CharField(max_length=10, choices=USER_TYPES, default='client')
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username