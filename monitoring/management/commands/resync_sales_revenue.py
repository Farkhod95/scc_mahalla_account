"""
Savdo tushumi (faktura + OKKM) ni TO'LIQ tozalab, qaytadan yig'adi.

Revenue tin tashkilot turiga qarab olinadi (revenue_sync._resolve_tin):
  YTT -> pinfl (leader_jshshir),  MCHJ -> stir.

DIQQAT: soliq API faqat ruxsat etilgan server IP sidan ochiladi — bu komanda
SHU serverda ishlatilishi kerak (localda DNS yo'q). OKKM backfill SEKIN
(har kun x har terminal alohida so'rov), shuning uchun keng oraliq uzoq davom etadi.

Ishlatish:
    python manage.py resync_sales_revenue                  # joriy yil 1-yanvardan bugungacha
    python manage.py resync_sales_revenue --year 2026
    python manage.py resync_sales_revenue --from 01.01.2026 --to 19.06.2026
    python manage.py resync_sales_revenue --no-clear        # tozalamaydi (faqat upsert)
    python manage.py resync_sales_revenue --factura-only    # faqat faktura
    python manage.py resync_sales_revenue --okkm-only       # faqat OKKM
"""
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from monitoring.models import FacturaRevenueDaily, OkkmRevenueDaily
from monitoring.services.okkm_revenue_sync import sync_okkm_revenue
from monitoring.services.revenue_sync import sync_factura_revenue


class Command(BaseCommand):
    help = "FacturaRevenueDaily + OkkmRevenueDaily ni to'liq tozalab qaytadan yig'adi."

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, help="Yil (default: joriy yil)")
        parser.add_argument("--from", dest="period_from", help="dd.mm.yyyy (default: 01.01.yil)")
        parser.add_argument("--to", dest="period_to", help="dd.mm.yyyy (default: bugun yoki 31.12.yil)")
        parser.add_argument("--no-clear", action="store_true", help="Tozalamaydi (faqat upsert)")
        parser.add_argument("--factura-only", action="store_true", help="Faqat faktura")
        parser.add_argument("--okkm-only", action="store_true", help="Faqat OKKM")

    def handle(self, *args, **opts):
        factura_only = opts.get("factura_only", False)
        okkm_only = opts.get("okkm_only", False)
        if factura_only and okkm_only:
            raise CommandError("--factura-only va --okkm-only birga berilmaydi.")
        do_factura = not okkm_only
        do_okkm = not factura_only

        today = date.today()
        year = opts.get("year") or today.year
        period_from = opts.get("period_from") or f"01.01.{year}"
        period_to = opts.get("period_to") or (
            today.strftime("%d.%m.%Y") if year == today.year else f"31.12.{year}"
        )
        do_clear = not opts.get("no_clear", False)

        if do_clear:
            if do_factura:
                f_del = FacturaRevenueDaily.objects.all().delete()[0]
                self.stdout.write(self.style.WARNING(f"FacturaRevenueDaily tozalandi: {f_del}"))
            if do_okkm:
                o_del = OkkmRevenueDaily.objects.all().delete()[0]
                self.stdout.write(self.style.WARNING(f"OkkmRevenueDaily tozalandi: {o_del}"))

        if do_factura:
            self.stdout.write(f"Faktura yig'ilmoqda ({period_from} .. {period_to})...")
            f = sync_factura_revenue(period_from=period_from, period_to=period_to)
            self.stdout.write(self.style.SUCCESS(
                f"Faktura: tenants={f.tenants}, nofaol_skip={f.skipped_inactive}, "
                f"tin_li={f.with_tin}, kun={f.days_written}, xato={f.errors}"
            ))

        if do_okkm:
            self.stdout.write(f"OKKM yig'ilmoqda ({period_from} .. {period_to}) — sekin...")
            o = sync_okkm_revenue(period_from=period_from, period_to=period_to, clear=False)
            self.stdout.write(self.style.SUCCESS(
                f"OKKM: tenants={o.tenants}, nofaol_skip={o.skipped_inactive}, "
                f"tin_li={o.with_tin}, kun={o.days_written}, xato={o.errors}"
            ))

        self.stdout.write(self.style.SUCCESS("Savdo tushumi qaytadan yig'ildi."))
