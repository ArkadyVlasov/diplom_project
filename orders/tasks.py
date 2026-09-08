from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_confirmation(order_id):
    from .models import Order
    order = Order.objects.get(id=order_id)
    subject = f'Подтверждение заказа №{order.id}'
    message = f'Ваш заказ №{order.id} на сумму {order.total} руб. принят.\nСпасибо за покупку!'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [order.user.email])

@shared_task
def send_order_notification_to_admin(order_id):
    from .models import Order
    order = Order.objects.get(id=order_id)
    
    # Используем order.contact (вместо order.address)
    address = str(order.contact) if order.contact else 'Адрес не указан'
    
    subject = f'Новый заказ №{order.id}'
    message = (
        f'Поступил новый заказ №{order.id} от {order.user.username}\n'
        f'Сумма: {order.total}\n'
        f'Адрес: {address}'
    )
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
    send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])