from django.urls import path
from .views import PartnerUpdateView, PartnerStateView, PartnerOrdersView

app_name = 'partner'

urlpatterns = [
    path('partner/update/', PartnerUpdateView.as_view(), name='partner-update'),
    path('partner/state/', PartnerStateView.as_view(), name='partner-state'),
    path('partner/orders/', PartnerOrdersView.as_view(), name='partner-orders'),
]