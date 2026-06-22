from datetime import date

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import TaxRevenue, TaxRevenueMonthly

# Dashboard bilan bir xil — faqat shu 3 kod ko'rsatiladi.
REPORT_TAX_CODES = [
    (1, "QQS"),
    (32, "Foyda solig'i"),
    (100, "Aylanma soliq"),
]


class TaxRevenueReportView(APIView):
    """
    Soliq tushumi — QQS(1), Foyda solig'i(32), Aylanma soliq(100).

      - oy berilmasa: TaxRevenue snapshot'idan (kunlik/oylik/yillik).
      - ?month=1..12 (+ ?year=): TaxRevenueMonthly (oylik tarix) jadvalidan shu oy.

    Ikkala manba ham celery (sync_tax_revenue / sync_tax_revenue_monthly) bilan
    to'ldiriladi — endpoint jonli soliqqa bormaydi.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")
        if month:
            return self._month_report(request, month)
        return self._snapshot_report()

    # ------------------------------------------------------------------
    def _snapshot_report(self):
        agg = {
            r["tax_code"]: r
            for r in TaxRevenue.objects.values("tax_code").annotate(
                d=Sum("dtd_pay"), m=Sum("mtd_pay"), y=Sum("ytd_pay")
            )
        }
        items = []
        td = tm = ty = 0.0
        for code, name in REPORT_TAX_CODES:
            row = agg.get(code, {})
            d = float(row.get("d") or 0)
            m = float(row.get("m") or 0)
            y = float(row.get("y") or 0)
            td += d
            tm += m
            ty += y
            items.append({
                "code": code, "name": name,
                "daily": round(d, 2), "monthly": round(m, 2), "yearly": round(y, 2),
            })
        return Response({
            "items": items,
            "total": {"daily": round(td, 2), "monthly": round(tm, 2), "yearly": round(ty, 2)},
        })

    # ------------------------------------------------------------------
    def _month_report(self, request, month_raw):
        try:
            month = int(month_raw)
        except (TypeError, ValueError):
            return Response({"detail": "month 1..12 bo'lishi kerak"}, status=400)
        if not 1 <= month <= 12:
            return Response({"detail": "month 1..12 bo'lishi kerak"}, status=400)

        today = date.today()
        try:
            year = int(request.query_params.get("year") or today.year)
        except (TypeError, ValueError):
            year = today.year

        codes = [c for c, _ in REPORT_TAX_CODES]
        agg = {
            r["tax_code"]: r["s"]
            for r in TaxRevenueMonthly.objects
            .filter(year=year, month=month, tax_code__in=codes)
            .values("tax_code").annotate(s=Sum("pay_tax"))
        }

        items = []
        total = 0.0
        for code, name in REPORT_TAX_CODES:
            v = round(float(agg.get(code) or 0), 2)
            total += v
            items.append({"code": code, "name": name, "monthly": v})

        return Response({
            "year": year,
            "month": month,
            "items": items,
            "total": round(total, 2),
        })
