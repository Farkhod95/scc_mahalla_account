"""
OKKM (NKM cheklar) kunlik tushumini OkkmRevenueDaily ga yig'adi.

Ishlatish (soliq API ochiladigan serverda):
    # faqat bugun (kunlik — celery beat ham shuni qiladi)
    python manage.py sync_okkm_revenue

    # BACKFILL: o'tgan kunlarni to'ldirish (BIR MARTA, sekin — har kun x har tenant so'rov)
    python manage.py sync_okkm_revenue --from 01.01.2026 --to 09.06.2026

Backfilldan keyin kunlik beat (sync-okkm-revenue-daily) bugunni qo'shib boradi.
"""
from django.core.management.base import BaseCommand

from monitoring.services.okkm_revenue_sync import sync_okkm_revenue


class Command(BaseCommand):
    help = "OKKM (NKM cheklar) kunlik tushumini OkkmRevenueDaily ga yig'adi."

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="period_from", help="dd.mm.yyyy (default: bugun)")
        parser.add_argument("--to", dest="period_to", help="dd.mm.yyyy (default: bugun)")

    def handle(self, *args, **opts):
        self.stdout.write("OKKM kunlik tushumi yig'ilmoqda...")
        stats = sync_okkm_revenue(
            period_from=opts.get("period_from"),
            period_to=opts.get("period_to"),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: tenants={stats.tenants}, nofaol_skip={stats.skipped_inactive}, "
            f"tin_li={stats.with_tin}, yozilgan_kun={stats.days_written}, xato={stats.errors}"
        ))
