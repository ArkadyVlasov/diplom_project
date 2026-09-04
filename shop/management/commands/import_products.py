import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from shop.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from users.models import User

class Command(BaseCommand):
    help = 'Import products from YAML file for a specific shop'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to YAML file')
        parser.add_argument('--user_id', type=int, required=True, help='ID of the supplier user')

    def handle(self, *args, **options):
        file_path = options['file_path']
        user_id = options['user_id']

        try:
            user = User.objects.get(id=user_id, user_type='supplier')
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Supplier with id {user_id} not found'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data:
            self.stderr.write(self.style.ERROR('Empty YAML file'))
            return

        shop_name = data.get('shop')
        if not shop_name:
            self.stderr.write(self.style.ERROR('No shop name in YAML'))
            return

        # Создаём или получаем магазин
        shop, created = Shop.objects.get_or_create(
            user=user,
            defaults={'name': shop_name}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created new shop: {shop_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updating existing shop: {shop_name}'))

        # Импорт категорий
        categories_data = data.get('categories', [])
        categories_map = {}
        with transaction.atomic():
            for cat_data in categories_data:
                cat_id = cat_data.get('id')
                cat_name = cat_data.get('name')
                if not cat_id or not cat_name:
                    continue
                category, _ = Category.objects.get_or_create(name=cat_name)
                category.shops.add(shop)
                categories_map[cat_id] = category
                self.stdout.write(f'  Category: {cat_name}')

            # Импорт товаров
            goods = data.get('goods', [])
            for item in goods:
                product_name = item.get('name')
                category_id = item.get('category')
                if not product_name or category_id not in categories_map:
                    continue

                product, _ = Product.objects.get_or_create(
                    name=product_name,
                    category=categories_map[category_id]
                )

                # Создаём ProductInfo
                product_info, created = ProductInfo.objects.update_or_create(
                    product=product,
                    shop=shop,
                    defaults={
                        'external_id': item.get('id', ''),
                        'quantity': item.get('quantity', 0),
                        'price': item.get('price', 0.0),
                        'price_rrc': item.get('price_rrc', 0.0),
                    }
                )

                # Параметры (характеристики)
                params = item.get('parameters', {})
                for param_name, param_value in params.items():
                    param, _ = Parameter.objects.get_or_create(name=param_name)
                    ProductParameter.objects.update_or_create(
                        product_info=product_info,
                        parameter=param,
                        defaults={'value': str(param_value)}
                    )

                self.stdout.write(f'  Product: {product_name} (price: {item.get("price")})')

        self.stdout.write(self.style.SUCCESS('Import completed successfully'))