"""
Django settings for config project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# =================================================
# БЕЗОПАСНОСТЬ И ОТЛАДКА
# =================================================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-...')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# =================================================
# ПРИЛОЖЕНИЯ
# =================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',
    'djoser',

    'users',       # кастомная модель пользователя
    'shop',        # товары, категории, магазины
    'cart',        # корзина
    'orders',      # заказы
    'contacts',    # контакты (адреса доставки)
    'partner',
]

AUTH_USER_MODEL = 'users.User'

# =================================================
# MIDDLEWARE И URL-КОНФИГУРАЦИЯ
# =================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =================================================
# БАЗА ДАННЫХ (по умолчанию SQLite)
# =================================================
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# =================================================
# ВАЛИДАЦИЯ ПАРОЛЕЙ
# =================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =================================================
# ИНТЕРНАЦИОНАЛИЗАЦИЯ
# =================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =================================================
# СТАТИЧЕСКИЕ ФАЙЛЫ
# =================================================
STATIC_URL = 'static/'

# =================================================
# DRF НАСТРОЙКИ
# =================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

# =================================================
# DJOSER (регистрация, активация, сброс пароля)
# =================================================
DJOSER = {
    'USER_ID_FIELD': 'id',
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': True,          # отправлять письмо для активации
    'ACTIVATION_URL': 'activate/{uid}/{token}',  # URL для активации
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/{uid}/{token}',
    'SERIALIZERS': {
        'user_create': 'djoser.serializers.UserCreateSerializer',
    },
}

# =================================================
# НАСТРОЙКИ EMAIL (реальная отправка через SMTP)
# =================================================

# Загружаем переменные из .env
from dotenv import load_dotenv
load_dotenv()

# Email settings (для разработки — письма выводятся в консоль)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')      # или smtp.gmail.com
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))              # 465 для SSL, 587 для TLS
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Адрес администратора для уведомлений о заказах
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')

# =================================================
# CELERY (асинхронные задачи)
# =================================================
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'