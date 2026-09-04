from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as authtoken_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/token/', authtoken_views.obtain_auth_token, name='api_token_auth'),
    path('api/products/', include('shop.urls')),
    path('api/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
]