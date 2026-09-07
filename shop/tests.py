from celery import shared_task
from django.core.management import call_command
import requests
import tempfile
import os

@shared_task
def import_products_task(url, user_id):
    """
    Асинхронная задача для импорта товаров из YAML-файла, доступного по URL.
    Скачивает файл, сохраняет во временный файл, вызывает команду import_products,
    затем удаляет временный файл.
    """
    # 1. Скачиваем файл
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Не удалось загрузить файл: статус {response.status_code}")

    # 2. Сохраняем содержимое во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(response.text)
        temp_path = f.name

    try:
        # 3. Вызываем команду импорта (передаём путь к файлу и ID пользователя)
        call_command('import_products', temp_path, user_id=user_id)
    finally:
        # 4. Удаляем временный файл
        os.unlink(temp_path)