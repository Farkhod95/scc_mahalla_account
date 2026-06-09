"""
Ijara (rent) integratsiyasidan ijarachilarni ShopTenant ga sync qiladi.

Ishlatish (soliq ochiladigan serverda):
    python manage.py sync_tenants_rent
    python manage.py sync_tenants_rent --shop 59
"""
from django.core.management.base import BaseCommand

from monitoring.services.rent_sync import sync_tenants_from_rent


class Command(BaseCommand):
    help = "Ijara API'dan ijarachilarni (ShopTenant) sync qiladi."

    def add_arguments(self, parser):
        parser.add_argument("--shop", type=int, default=None, help="Faqat bitta do'kon id")

    def handle(self, *args, **opts):
        self.stdout.write("Ijara integratsiyasidan ijarachilar yig'ilmoqda...")
        stats = sync_tenants_from_rent(only_shop_id=opts.get("shop"))
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: do'konlar={stats.shops}, egasi+kadastrli={stats.with_owner_cadastr}, "
            f"yaratildi={stats.tenants_created}, yangilandi={stats.tenants_updated}, "
            f"nofaol_qilindi={stats.tenants_deactivated}, xato={stats.errors}"
        ))
