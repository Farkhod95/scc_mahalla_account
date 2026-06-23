"""
Soliq tushumi — tashkilotlar bo'yicha OYLIK Excel hisobot.

Har bir tashkilot (ShopTenant) qator, har oy (Yan..Dek) ustun. Qiymat = shu oyda
TO'LANGAN soliq (TaxRevenueMonthly.pay_tax), QQS(1) + Foyda solig'i(32) +
Aylanma soliq(100) yig'indisi — dashboard va /reports/tax-revenue bilan bir xil 3 kod.

Ko'rinish/uslub savdo tushumi Excel bilan bir xil (_revenue_excel).
Identifikator: YTT -> PINFL, MCHJ -> STIR.

GET /api/v1/reports/tax-revenue/excel?year=2026
  ?year= berilmasa — joriy yil.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from monitoring.models import TaxRevenueMonthly
from reports.views._revenue_excel import (
    build_monthly_workbook,
    collect_tenant_info,
    rows_from_revenue,
    xlsx_response,
)

# Dashboard / tax-revenue bilan bir xil — shu 3 kod yig'indisi "soliq tushumi".
REPORT_TAX_CODES = [1, 32, 100]  # QQS, Foyda solig'i, Aylanma soliq


class TaxRevenueExcelView(APIView):
    """Tashkilotlar bo'yicha oylik soliq tushumi (QQS + Foyda + Aylanma) — .xlsx."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get("year") or date.today().year)
        except (TypeError, ValueError):
            year = date.today().year

        # tin x oy bo'yicha to'langan soliqni (3 kod yig'indisi) DB da yig'amiz.
        # revenue[tin][month_index 0..11] = Decimal soliq
        revenue: dict[str, list[Decimal]] = defaultdict(lambda: [Decimal(0)] * 12)
        for r in (
            TaxRevenueMonthly.objects
            .filter(year=year, tax_code__in=REPORT_TAX_CODES)
            .values("tin", "month")
            .annotate(s=Sum("pay_tax"))
        ):
            tin = (r["tin"] or "").strip()
            if tin and 1 <= (r["month"] or 0) <= 12:
                revenue[tin][r["month"] - 1] += r["s"] or Decimal(0)

        rows = rows_from_revenue(revenue, collect_tenant_info())

        title = (
            f"Soliq tushumi (QQS + Foyda + Aylanma) — {year}-yil, "
            f"tashkilotlar bo'yicha oylik (so'm)"
        )
        wb = build_monthly_workbook(year, rows, title)
        return xlsx_response(wb, f"soliq_tushumi_{year}.xlsx")
