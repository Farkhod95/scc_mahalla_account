"""
Dashboard: savdo va soliq tushumi grafigi (vaqt bo'yicha).

GET /api/v1/reports/revenue-chart?range=week|month|year   (default: week)

Manba — FacturaRevenueDaily (faktura'dan davriy yig'ilgan tarix).
Qiymatlar mln so'mda (raw so'm / 1 000 000).
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import FacturaRevenueDaily

WEEKDAY_LABELS = ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"]  # Mon..Sun
MONTH_LABELS = ["Yan", "Fev", "Mar", "Apr", "May", "Iyn",
                "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"]
MLN = Decimal("1000000")


class RevenueChartView(APIView):
    permission_classes = [IsAuthenticated]

    def _to_mln(self, value):
        return float((Decimal(value or 0) / MLN).quantize(Decimal("0.01")))

    def _sum_by_date(self, start, end):
        rows = (
            FacturaRevenueDaily.objects
            .filter(date__gte=start, date__lte=end)
            .values("date")
            .annotate(s=Sum("sales"), t=Sum("tax"))
        )
        return {r["date"]: (r["s"] or 0, r["t"] or 0) for r in rows}

    def _week(self, today):
        monday = today - timedelta(days=today.weekday())
        days = [monday + timedelta(days=i) for i in range(7)]
        by_date = self._sum_by_date(days[0], days[-1])
        sales, tax = [], []
        for i, d in enumerate(days):
            s, t = by_date.get(d, (0, 0))
            sales.append({"label": WEEKDAY_LABELS[i], "value": self._to_mln(s)})
            tax.append({"label": WEEKDAY_LABELS[i], "value": self._to_mln(t)})
        return sales, tax

    def _month(self, today):
        # oxirgi 7 oy (joriy oy bilan)
        months = []
        y, m = today.year, today.month
        for _ in range(7):
            months.append((y, m))
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        months.reverse()

        start = date(months[0][0], months[0][1], 1)
        by_date = self._sum_by_date(start, today)

        buckets = {(y, m): [Decimal(0), Decimal(0)] for (y, m) in months}
        for d, (s, t) in by_date.items():
            key = (d.year, d.month)
            if key in buckets:
                buckets[key][0] += Decimal(s)
                buckets[key][1] += Decimal(t)

        sales, tax = [], []
        for (y, m) in months:
            label = MONTH_LABELS[m - 1]
            sales.append({"label": label, "value": self._to_mln(buckets[(y, m)][0])})
            tax.append({"label": label, "value": self._to_mln(buckets[(y, m)][1])})
        return sales, tax

    def _year(self, today):
        years = [today.year - i for i in range(6, -1, -1)]
        start = date(years[0], 1, 1)
        by_date = self._sum_by_date(start, today)

        buckets = {y: [Decimal(0), Decimal(0)] for y in years}
        for d, (s, t) in by_date.items():
            if d.year in buckets:
                buckets[d.year][0] += Decimal(s)
                buckets[d.year][1] += Decimal(t)

        sales, tax = [], []
        for y in years:
            sales.append({"label": str(y), "value": self._to_mln(buckets[y][0])})
            tax.append({"label": str(y), "value": self._to_mln(buckets[y][1])})
        return sales, tax

    def get(self, request, *args, **kwargs):
        rng = request.query_params.get("range", "week").lower()
        today = date.today()

        if rng == "month":
            sales, tax = self._month(today)
        elif rng == "year":
            sales, tax = self._year(today)
        else:
            rng = "week"
            sales, tax = self._week(today)

        return Response({
            "range": rng,
            "unit": "mln so'm",
            "sales_revenue": {"title": "Savdo tushumlari", "chart": sales},
            "tax_revenue": {"title": "Soliq tushumlari", "chart": tax},
        })
