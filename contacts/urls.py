from django.urls import path
from .views import ContactListCreateView, ContactDetailView

app_name = 'contacts'

urlpatterns = [
    path('user/contact/', ContactListCreateView.as_view(), name='contact-list'),
    path('user/contact/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
]