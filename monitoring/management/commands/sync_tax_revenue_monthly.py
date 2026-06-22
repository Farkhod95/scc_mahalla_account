"""
Soliq tushumi oylik tarixini (TaxRevenueMonthly) yig'adi.

    python manage.py sync_tax_revenue_monthly                 # joriy yil, barcha oylar (backfill)
    python manage.py sync_tax_revenue_monthly --year 2026
    python manage.py sync_tax_revenue_monthly --only-current  # faqat joriy oy (kunlik celery)
    python manage.py sync_tax_revenue_monthly --include-inactive

Og'ir (har tin x kod x oy = 1 so'rov) — soliq API ochiladigan serverda ishlating.
"""
from django.core.management.base import BaseCommand

from monitoring.services.tax_revenue_monthly_sync import sync_tax_revenue_monthly


class Command(BaseCommand):
    help = "Soliq tushumi oylik tarixini (TaxRevenueMonthly) yig'adi."

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, default=None, help="Yil (default: joriy)")
        parser.add_argument("--only-current", action="store_true", help="Faqat joriy oy")
        parser.add_argument("--include-inactive", action="store_true", help="Nofaol tenantlarni ham")

    def handle(self, *args, **opts):
        self.stdout.write("Soliq oylik tarixi yig'ilmoqda...")
        stats = sync_tax_revenue_monthly(
            year=opts.get("year"),
            only_current=opts.get("only_current", False),
            include_inactive=opts.get("include_inactive", False),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: tenants={stats.tenants}, tin_li={stats.with_tin}, "
            f"yozilgan={stats.rows_written}, xato={stats.errors}"
        ))
