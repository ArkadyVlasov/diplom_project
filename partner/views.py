from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.management import call_command
from django.conf import settings
from shop.models import Shop
from orders.models import Order, OrderItem
from .serializers import ShopStateSerializer, PartnerOrderSerializer
from shop.tasks import import_products_task  # задача Celery для импорта


class PartnerUpdateView(views.APIView):
    """
    Обновление прайса поставщика (импорт товаров по URL).
    Принимает JSON: {"url": "https://example.com/price.yaml"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.type != 'shop':
            return Response(
                {"error": "Только поставщики могут обновлять прайс"},
                status=status.HTTP_403_FORBIDDEN
            )

        url = request.data.get('url')
        if not url:
            return Response(
                {"error": "Не указан URL файла прайса"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Запускаем задачу импорта асинхронно (Celery)
        # Передаём URL и ID пользователя
        import_products_task.delay(url, user.id)

        return Response(
            {"status": "Импорт запущен в фоновом режиме"},
            status=status.HTTP_202_ACCEPTED
        )


class PartnerStateView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и изменение статуса магазина (вкл/выкл приём заказов).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ShopStateSerializer

    def get_object(self):
        user = self.request.user
        if user.type != 'shop':
            return None
        # Предполагаем, что у пользователя-поставщика есть ровно один магазин
        shop = Shop.objects.filter(user=user).first()
        return shop

    def get(self, request, *args, **kwargs):
        shop = self.get_object()
        if not shop:
            return Response(
                {"error": "У вас нет магазина"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(shop)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        shop = self.get_object()
        if not shop:
            return Response(
                {"error": "У вас нет магазина"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(shop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PartnerOrdersView(generics.ListAPIView):
    """
    Список заказов, содержащих товары текущего поставщика.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PartnerOrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.type != 'shop':
            return Order.objects.none()

        # Получаем ID товаров (ProductInfo) этого поставщика
        shop = Shop.objects.filter(user=user).first()
        if not shop:
            return Order.objects.none()

        # Находим все позиции заказов, где товар принадлежит этому магазину
        order_ids = OrderItem.objects.filter(
            product_info__shop=shop
        ).values_list('order_id', flat=True).distinct()

        return Order.objects.filter(id__in=order_ids).prefetch_related(
            'items__product_info__product',
            'items__product_info__shop',
            'contact'
        )