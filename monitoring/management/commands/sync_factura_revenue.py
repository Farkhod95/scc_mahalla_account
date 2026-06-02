"""
Faktura tushumini FacturaRevenueDaily ga yig'adi (dashboard grafigi manbasi).

Ishlatish (soliq API ochiladigan serverda):
    # joriy yil boshidan bugungacha
    python manage.py sync_factura_revenue

    # aniq davr
    python manage.py sync_factura_revenue --from 01.01.2026 --to 28.02.2026
"""
from django.core.management.base import BaseCommand

from monitoring.services.revenue_sync import sync_factura_revenue


class Command(BaseCommand):
    help = "Soliq faktura'sidan kunlik savdo/soliq tushumini yig'adi."

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="period_from", help="dd.mm.yyyy (default: 01.01.joriy_yil)")
        parser.add_argument("--to", dest="period_to", help="dd.mm.yyyy (default: bugun)")

    def handle(self, *args, **opts):
        self.stdout.write("Faktura tushumi yig'ilmoqda...")
        stats = sync_factura_revenue(
            period_from=opts.get("period_from"),
            period_to=opts.get("period_to"),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: tenants={stats.tenants}, tin_li={stats.with_tin}, "
            f"yozilgan_kun={stats.days_written}, xato={stats.errors}"
        ))
