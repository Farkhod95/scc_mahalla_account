"""
Savdo tushumlari (faktura + OKKM) — tashkilotlar bo'yicha OYLIK Excel hisobot.

Har bir tashkilot (ShopTenant) qator, har oy (Yan..Dek) ustun. Qiymat =
FacturaRevenueDaily.sales + OkkmRevenueDaily.turnover (xom so'm), shu oyda
yig'ilgan. Bu dashboarddagi "Savdo tushumlari" bilan bir xil manba.

Ko'rinish/uslub umumiy yordamchidan (_revenue_excel) — soliq tushumi Excel bilan
bir xil jadval. Identifikator: YTT -> PINFL, MCHJ -> STIR.

GET /api/v1/reports/sales-revenue/excel?year=2026&source=factura|okkm|both
  ?year= berilmasa — joriy yil. ?source= berilmasa — both.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from monitoring.models import FacturaRevenueDaily, OkkmRevenueDaily
from reports.views._revenue_excel import (
    build_monthly_workbook,
    collect_tenant_info,
    rows_from_revenue,
    xlsx_response,
)


class SalesRevenueExcelView(APIView):
    """Tashkilotlar bo'yicha oylik savdo tushumlari (faktura + OKKM) — .xlsx."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get("year") or date.today().year)
        except (TypeError, ValueError):
            year = date.today().year

        # ?source=factura | okkm | both (default both)
        source = (request.query_params.get("source") or "both").lower()
        if source not in ("factura", "okkm", "both"):
            source = "both"

        # 1) Tanlangan manba(lar)ni tin x oy bo'yicha DB da yig'amiz.
        #    revenue[tin][month_index 0..11] = Decimal savdo
        revenue: dict[str, list[Decimal]] = defaultdict(lambda: [Decimal(0)] * 12)

        if source in ("factura", "both"):
            for r in (
                FacturaRevenueDaily.objects
                .filter(date__year=year)
                .values("seller_tin", "date__month")
                .annotate(s=Sum("sales"))
            ):
                tin = (r["seller_tin"] or "").strip()
                if tin:
                    revenue[tin][r["date__month"] - 1] += r["s"] or Decimal(0)

        if source in ("okkm", "both"):
            for r in (
                OkkmRevenueDaily.objects
                .filter(date__year=year)
                .values("tin", "date__month")
                .annotate(o=Sum("turnover"))
            ):
                tin = (r["tin"] or "").strip()
                if tin:
                    revenue[tin][r["date__month"] - 1] += r["o"] or Decimal(0)

        # 2) tin -> tashkilot ma'lumoti, 3) tartiblangan qatorlar (umumiy yordamchi).
        rows = rows_from_revenue(revenue, collect_tenant_info())

        source_label = {
            "factura": "faktura",
            "okkm": "OKKM",
            "both": "faktura + OKKM",
        }.get(source, "faktura + OKKM")
        title = (
            f"Savdo tushumlari ({source_label}) — {year}-yil, "
            f"tashkilotlar bo'yicha oylik (so'm)"
        )
        wb = build_monthly_workbook(year, rows, title)
        return xlsx_response(wb, f"savdo_tushumlari_{source}_{year}.xlsx")
