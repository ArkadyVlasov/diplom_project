from django.urls import path
from .views import CartView, CartItemDeleteView

app_name = 'cart'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart-list'),
    path('cart/<int:pk>/', CartItemDeleteView.as_view(), name='cart-delete'),
]