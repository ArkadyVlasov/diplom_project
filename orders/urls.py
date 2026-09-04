from django.urls import path
from .views import OrderListCreateView, OrderConfirmView, OrderStatusUpdateView

app_name = 'orders'

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list'),
    path('confirm/', OrderConfirmView.as_view(), name='order-confirm'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]