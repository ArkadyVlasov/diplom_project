from celery import shared_task
from django.core.management import call_command
import tempfile
import requests
import os

@shared_task
def import_products_task(url, user_id):
    """
    Задача для импорта товаров из YAML-файла по URL.
    Скачивает файл, сохраняет во временный файл и вызывает команду импорта.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f'Ошибка скачивания файла: {e}')

    # Сохраняем во временный файл
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml', delete=False) as f:
        f.write(response.text)
        temp_path = f.name

    try:
        # Вызываем команду импорта
        call_command('import_products', temp_path, user_id=user_id)
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.unlink(temp_path)