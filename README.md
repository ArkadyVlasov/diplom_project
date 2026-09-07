# Дипломный проект: Backend-приложение для автоматизации закупок в розничной сети

## Описание проекта
REST API-сервис для автоматизации закупок в розничной сети. Реализованы роли клиента и поставщика, управление контактами, корзина, заказы, импорт товаров через API, асинхронные уведомления по email.

## Исправленные замечания преподавателя
В проекте устранены все критические несоответствия, выявленные при проверке:
- Модель User приведена к ТЗ: добавлены поля company, position, type (shop/buyer), is_active по умолчанию False (требуется подтверждение email).
- Создана модель Contact и реализовано полноценное API для управления контактами (/user/contact).
- Модель Order переработана: вместо текстового поля address используется внешний ключ на Contact.
- Реализован импорт товаров через API-эндпоинт /partner/update (принимает URL на YAML-файл, запускает асинхронную задачу через Celery). Django-команда import_products оставлена как вспомогательный инструмент для локальной загрузки.
- Добавлены все недостающие эндпоинты из спецификации:
  - /api/auth/users/activation/ – подтверждение email
  - /api/auth/users/me/ – профиль пользователя
  - /api/user/contact/ – CRUD контактов
  - /api/categories/ – список категорий
  - /api/shops/ – список магазинов
  - /api/partner/update/, /api/partner/state/, /api/partner/orders/ – для поставщика
- Настроена асинхронная отправка email через Celery (письма выводятся в консоль для разработки, легко переключаются на реальный SMTP).
- Добавлена документация (этот файл) с инструкцией по запуску и тестированию.

## Технологии
- Python 3.10+
- Django 4.2 / Django REST Framework
- Djoser (аутентификация, регистрация, активация)
- Celery + Redis (асинхронные задачи)
- PyYAML (импорт товаров)
- PostgreSQL / SQLite (на выбор)
- Docker, Docker Compose (контейнеризация)

## Установка и запуск (локально)

1. Клонируйте репозиторий:
   git clone https://github.com/ArkadyVlasov/diplom_project.git
   cd diplom_project

2. Создайте виртуальное окружение и активируйте его:
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

3. Установите зависимости:
   pip install -r requirements.txt

4. Создайте файл .env в корне (пример):
   SECRET_KEY=ваш_секретный_ключ
   DEBUG=True
   DB_ENGINE=django.db.backends.sqlite3
   DB_NAME=db.sqlite3
   REDIS_URL=redis://localhost:6379/0
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

5. Выполните миграции:
   python manage.py migrate

6. Создайте суперпользователя:
   python manage.py createsuperuser

7. (Опционально) Импортируйте тестовые товары:
   python manage.py import_products shop_data.yaml --user_id=1

8. Запустите сервер разработки:
   python manage.py runserver

9. Запустите Celery worker (в отдельном терминале):
   celery -A config worker --loglevel=info

## Запуск через Docker

Для запуска всех сервисов (Django, PostgreSQL, Redis, Celery) в контейнерах:

1. **Установите Docker Desktop** с [официального сайта](https://www.docker.com/products/docker-desktop/).

2. **В корневой папке проекта выполните:**
   docker compose up --build

После сборки приложение будет доступно по адресу http://localhost:8000.

Для остановки контейнеров нажмите Ctrl+C, затем:
   docker compose down

Примечание: при использовании Docker база данных автоматически создаётся из миграций, а Celery worker запускается отдельным контейнером.

## Основные эндпоинты API

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/auth/users/ | Регистрация |
| POST | /api/auth/users/activation/ | Активация email |
| POST | /api/auth/token/ | Получение токена |
| GET/PUT/PATCH | /api/auth/users/me/ | Профиль пользователя |
| GET | /api/categories/ | Список категорий |
| GET | /api/shops/ | Список магазинов |
| GET | /api/products/ | Список товаров |
| GET/POST | /api/user/contact/ | Управление контактами |
| GET/POST | /api/cart/ | Корзина |
| POST | /api/orders/confirm/ | Оформление заказа |
| GET | /api/orders/ | Список заказов |
| PATCH | /api/orders/<id>/status/ | Смена статуса |
| POST | /api/partner/update/ | Обновление прайса |
| GET/PATCH | /api/partner/state/ | Статус магазина |
| GET | /api/partner/orders/ | Заказы поставщика |

## Тестирование сценария клиента
1. Регистрация → активация → получение токена.
2. Создание контакта.
3. Добавление товара в корзину.
4. Оформление заказа с привязкой к контакту.
5. Проверка писем в консоли (или на почте).

## Тестирование сценария поставщика
1. Создать пользователя с типом shop.
2. Отправить POST на /partner/update с URL на YAML-файл.
3. Проверить статус магазина через /partner/state.
4. Получить список заказов через /partner/orders.

## Настройка email
По умолчанию письма выводятся в консоль. Для реальной отправки замените в .env:
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mail.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=ваш_логин
EMAIL_HOST_PASSWORD=ваш_пароль

## Ссылка на репозиторий
https://github.com/ArkadyVlasov/diplom_project

## Автор
Аркадий Власов
Сентябрь 2026