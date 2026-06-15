"""
Soliq tushumini (company-account, payTax) kodlar bo'yicha TaxRevenue ga yig'adi.

Og'ir: har faol tin x 7 kod x 3 davr = 21 so'rov. Celery beat (sync-tax-revenue-daily)
ham shuni qiladi; bu command qo'lda ishga tushirish uchun (soliq API ochiladigan serverda).

    python manage.py sync_tax_revenue
"""
from django.core.management.base import BaseCommand

from monitoring.services.tax_revenue_sync import sync_tax_revenue


class Command(BaseCommand):
    help = "Soliq tushumini (kodlar bo'yicha payTax) TaxRevenue ga yig'adi."

    def handle(self, *args, **opts):
        self.stdout.write("Soliq tushumi yig'ilmoqda...")
        stats = sync_tax_revenue()
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: tenants={stats.tenants}, nofaol_skip={stats.skipped_inactive}, "
            f"tin_li={stats.with_tin}, yozilgan={stats.rows_written}, "
            f"o'chirilgan={stats.cleared}, xato={stats.errors}"
        ))
