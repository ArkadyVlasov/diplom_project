from celery import shared_task
from django.core.management import call_command

@shared_task
def import_products_task(file_path, user_id):
    call_command('import_products', file_path, user_id=user_id)