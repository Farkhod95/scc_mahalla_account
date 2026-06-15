from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from monitoring.models import TaxRevenue
from monitoring.services.tax_revenue_sync import TAX_CODES


class TaxRevenueReportView(APIView):
    """
    Soliq tushumi — kodlar (1, 32, 36, 38, 46, 100, 186) bo'yicha kunlik / oylik /
    yillik payTax (barcha faol ijarachilar yig'indisi).

    Ma'lumot TaxRevenue jadvalidan o'qiladi (celery sync to'ldiradi) — jonli soliqqa
    bormaydi. Javob:
      {
        "items": [{"code", "name", "daily", "monthly", "yearly"}, ...],
        "total": {"daily", "monthly", "yearly"}
      }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        agg = {
            r["tax_code"]: r
            for r in TaxRevenue.objects.values("tax_code").annotate(
                d=Sum("dtd_pay"), m=Sum("mtd_pay"), y=Sum("ytd_pay")
            )
        }

        items = []
        total_d = total_m = total_y = 0.0
        for code, name in TAX_CODES:
            row = agg.get(code, {})
            d = float(row.get("d") or 0)
            m = float(row.get("m") or 0)
            y = float(row.get("y") or 0)
            total_d += d
            total_m += m
            total_y += y
            items.append({
                "code": code,
                "name": name,
                "daily": round(d, 2),
                "monthly": round(m, 2),
                "yearly": round(y, 2),
            })

        return Response({
            "items": items,
            "total": {
                "daily": round(total_d, 2),
                "monthly": round(total_m, 2),
                "yearly": round(total_y, 2),
            },
        })
