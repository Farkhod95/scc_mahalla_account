"""
Soliq rekvizit + faktura tushumini ShopTenant maydonlariga yozadi.

shop-tenant API lari request thread da soliqqa bormasligi uchun ma'lumotni
oldindan bazaga to'ldiradi (birinchi marta qo'lda, keyin celery beat o'zi).

Ishlatish (soliq ochiladigan serverda):
    python manage.py sync_tenant_soliq
"""
from django.core.management.base import BaseCommand

from monitoring.services.tenant_soliq_sync import sync_tenant_soliq


class Command(BaseCommand):
    help = "Soliq rekvizit + faktura tushumini ShopTenant maydonlariga yozadi."

    def handle(self, *args, **opts):
        self.stdout.write("Soliqdan tenant ma'lumotlari yig'ilmoqda...")
        stats = sync_tenant_soliq()
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: tenantlar={stats.tenants}, yangilandi={stats.updated}, xato={stats.errors}"
        ))
