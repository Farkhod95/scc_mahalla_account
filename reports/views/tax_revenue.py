from datetime import date

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import TaxRevenueMonthly

# Dashboard bilan bir xil — faqat shu 3 kod ko'rsatiladi.
REPORT_TAX_CODES = [
    (1, "QQS"),
    (32, "Foyda solig'i"),
    (100, "Aylanma soliq"),
]


class TaxRevenueReportView(APIView):
    """
    Soliq tushumi — QQS(1), Foyda solig'i(32), Aylanma soliq(100).
    Manba: TaxRevenueMonthly (oylik tarix), dashboard bilan bir xil.

      - filtersiz:           monthly = joriy oy, yearly = joriy yil yig'indisi.
      - ?month=1..12&year=:  monthly = o'sha oy, yearly = o'sha yil yig'indisi.

    Ikkala holatda ham javob FORMATI bir xil:
      {"year","month","items":[{"code","name","daily","monthly","yearly"}], "total":{...}}
    daily — tax uchun bu yerda saqlanmaydi (dashboard savdodan hisoblaydi), 0.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        codes = [c for c, _ in REPORT_TAX_CODES]

        try:
            year = int(request.query_params.get("year") or today.year)
        except (TypeError, ValueError):
            year = today.year

        month_raw = request.query_params.get("month")
        if month_raw:
            try:
                month = int(month_raw)
            except (TypeError, ValueError):
                return Response({"detail": "month 1..12 bo'lishi kerak"}, status=400)
            if not 1 <= month <= 12:
                return Response({"detail": "month 1..12 bo'lishi kerak"}, status=400)
        else:
            month = today.month  # filtersiz -> joriy oy

        monthly_agg = self._by_code(year, codes, month=month)
        yearly_agg = self._by_code(year, codes, month=None)

        items = []
        td = tm = ty = 0.0
        for code, name in REPORT_TAX_CODES:
            d = 0.0
            m = float(monthly_agg.get(code) or 0)
            y = float(yearly_agg.get(code) or 0)
            td += d
            tm += m
            ty += y
            items.append({
                "code": code, "name": name,
                "daily": round(d, 2), "monthly": round(m, 2), "yearly": round(y, 2),
            })

        return Response({
            "year": year,
            "month": month,
            "items": items,
            "total": {"daily": round(td, 2), "monthly": round(tm, 2), "yearly": round(ty, 2)},
        })

    @staticmethod
    def _by_code(year, codes, month=None):
        qs = TaxRevenueMonthly.objects.filter(year=year, tax_code__in=codes)
        if month is not None:
            qs = qs.filter(month=month)
        return {
            r["tax_code"]: r["s"]
            for r in qs.values("tax_code").annotate(s=Sum("pay_tax"))
        }
