import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import requests
from django.core.cache import cache
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import ShopTenant, TaxRevenue
from monitoring.services import soliq_service

# Dashboard bilan bir xil — faqat shu 3 kod ko'rsatiladi.
REPORT_TAX_CODES = [
    (1, "QQS"),
    (32, "Foyda solig'i"),
    (100, "Aylanma soliq"),
]


class TaxRevenueReportView(APIView):
    """
    Soliq tushumi — QQS(1), Foyda solig'i(32), Aylanma soliq(100).

      - oy berilmasa: TaxRevenue snapshot'idan (kunlik/oylik/yillik) — tez, jonli emas.
      - ?month=1..12 (+ ?year=): tanlangan OY uchun soliq company-account'dan JONLI
        (faol STIR'lar bo'yicha parallel) hisoblanadi va 1 soat keshlanadi.

    Snapshot tarixiy oylarni saqlamaydi, shuning uchun aniq oy bo'yicha filter
    jonli so'rov bilan ishlaydi.
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

        cache_key = f"tax_revenue_month:{year}:{month}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        period_from = f"01.{month:02d}.{year}"
        last_day = calendar.monthrange(year, month)[1]
        end = date(year, month, last_day)
        if year == today.year and month == today.month:
            end = today  # joriy oy — bugungacha
        period_to = end.strftime("%d.%m.%Y")

        # Faol tenantlarning takrorsiz STIR'lari (company-account real STIR talab qiladi).
        tins = sorted({
            (s or "").strip()
            for s in ShopTenant.objects
            .exclude(activity_status=ShopTenant.ActivityStatus.INACTIVE)
            .exclude(stir__isnull=True).exclude(stir="")
            .values_list("stir", flat=True)
            if (s or "").strip()
        })

        codes = [c for c, _ in REPORT_TAX_CODES]
        sums = {c: 0.0 for c in codes}

        def fetch(args):
            tin, code = args
            try:
                data = soliq_service.get_company_account(tin, period_from, period_to, code) or {}
                return code, float(data.get("payTax") or 0)
            except (soliq_service.SoliqError, requests.RequestException):
                return code, 0.0

        tasks = [(tin, code) for tin in tins for code in codes]
        if tasks:
            with ThreadPoolExecutor(max_workers=15) as ex:
                for code, pay in ex.map(fetch, tasks):
                    sums[code] += pay

        items = []
        total = 0.0
        for code, name in REPORT_TAX_CODES:
            v = round(sums[code], 2)
            total += v
            items.append({"code": code, "name": name, "monthly": v})

        result = {
            "year": year,
            "month": month,
            "period": {"from": period_from, "to": period_to},
            "items": items,
            "total": round(total, 2),
        }
        cache.set(cache_key, result, 60 * 60)  # 1 soat
        return Response(result)
