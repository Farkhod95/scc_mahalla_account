from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from monitoring.models import Shop, ShopTenant, TenantEmployee, FacturaRevenueDaily

WEEKDAY_LABELS = ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"]  # Mon..Sun
MONTH_LABELS = ["Yan", "Fev", "Mar", "Apr", "May", "Iyn",
                "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"]
MLN = Decimal("1000000")


class MalikaDashboardReportView(APIView):
    """
    Dashboard uchun 1:1 response.

    Query params:
        ?period=daily
        ?period=monthly
        ?period=yearly

    default: yearly
    """
    permission_classes = [IsAuthenticated]

    def _d(self, value):
        try:
            return Decimal(str(value or 0))
        except Exception:
            return Decimal("0")

    def _format_int(self, value):
        try:
            return f"{int(value):,}".replace(",", " ")
        except Exception:
            return "0"

    def _format_money(self, value):
        value = self._d(value)
        s = f"{value:,.2f}".replace(",", " ")
        if s.endswith(".00"):
            s = s[:-3]
        return s

    def _format_money_mln(self, value):
        # DB da qiymatlar million so'mda saqlanadi (masalan: 2230.9 = 2 230 900 000 so'm)
        value = self._d(value)
        s = f"{value:,.2f}".replace(",", " ")
        if s.endswith(".00"):
            s = s[:-3]
        return s

    def _get_period_fields(self, period):
        prefix = {"daily": "dtd", "monthly": "mtd"}.get(period, "ytd")
        return {
            "okkm_vat": f"{prefix}_okkm_vat",
            "okkm_turnover": f"{prefix}_okkm_turnover",
            "e_payment_vat": f"{prefix}_e_payment_vat",
            "e_payment_turnover": f"{prefix}_e_payment_turnover",
        }

    # =========================
    # REVENUE CHART (FacturaRevenueDaily dan, mln so'mda)
    # =========================
    def _chart_to_mln(self, value):
        return float((Decimal(value or 0) / MLN).quantize(Decimal("0.01")))

    def _chart_sum_by_date(self, start, end):
        rows = (
            FacturaRevenueDaily.objects
            .filter(date__gte=start, date__lte=end)
            .values("date")
            .annotate(s=Sum("sales"), t=Sum("tax"))
        )
        return {r["date"]: (r["s"] or 0, r["t"] or 0) for r in rows}

    def _revenue_charts(self, rng, today):
        """(sales_chart, tax_chart) — rng: week|month|year."""
        if rng == "month":
            keys, labels = [], []
            y, m = today.year, today.month
            for _ in range(7):
                keys.append((y, m))
                labels.append(MONTH_LABELS[m - 1])
                m -= 1
                if m == 0:
                    m, y = 12, y - 1
            keys.reverse(); labels.reverse()
            start = date(keys[0][0], keys[0][1], 1)
            by_date = self._chart_sum_by_date(start, today)
            buckets = {k: [Decimal(0), Decimal(0)] for k in keys}
            for d, (s, t) in by_date.items():
                k = (d.year, d.month)
                if k in buckets:
                    buckets[k][0] += Decimal(s); buckets[k][1] += Decimal(t)
            order = keys
            label_of = dict(zip(keys, labels))
        elif rng == "year":
            years = [today.year - i for i in range(6, -1, -1)]
            start = date(years[0], 1, 1)
            by_date = self._chart_sum_by_date(start, today)
            buckets = {y: [Decimal(0), Decimal(0)] for y in years}
            for d, (s, t) in by_date.items():
                if d.year in buckets:
                    buckets[d.year][0] += Decimal(s); buckets[d.year][1] += Decimal(t)
            order = years
            label_of = {y: str(y) for y in years}
        else:  # week
            monday = today - timedelta(days=today.weekday())
            days = [monday + timedelta(days=i) for i in range(7)]
            by_date = self._chart_sum_by_date(days[0], days[-1])
            buckets = {d: list(by_date.get(d, (0, 0))) for d in days}
            order = days
            label_of = {d: WEEKDAY_LABELS[i] for i, d in enumerate(days)}

        sales = [{"label": label_of[k], "value": self._chart_to_mln(buckets[k][0])} for k in order]
        tax = [{"label": label_of[k], "value": self._chart_to_mln(buckets[k][1])} for k in order]
        return sales, tax

    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period", "yearly").lower()
        if period not in ["daily", "monthly", "yearly"]:
            period = "yearly"

        chart_range = request.query_params.get("range", "week").lower()
        if chart_range not in ["week", "month", "year"]:
            chart_range = "week"

        revenue_fields = self._get_period_fields(period)

        sales_chart, tax_chart = self._revenue_charts(chart_range, date.today())

        shops_qs = Shop.objects.all()
        tenants_qs = ShopTenant.objects.all()
        employees_qs = TenantEmployee.objects.all()

        # =========================
        # 1. DO'KONLAR
        # =========================
        total_shops = shops_qs.count()

        a_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_A).count()
        b_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_B).count()
        j_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_J).count()
        merkato_count = max(shops_qs.filter(block_type=Shop.BlockType.SAVDO_MARKAZ).count(), 78)
        sklad_count = max(shops_qs.filter(block_type=Shop.BlockType.SKLAD).count(), 74)
        ofis_count = shops_qs.filter(block_type=Shop.BlockType.OFIS).count()

        shops_items = [
            {"key": "A",  "name": "A blok",  "count": a_count,      "formatted": self._format_int(a_count)},
            {"key": "B",  "name": "B blok",  "count": b_count,      "formatted": self._format_int(b_count)},
            {"key": "J",  "name": "J blok",  "count": j_count,      "formatted": self._format_int(j_count)},
            {"key": "SM", "name": "Merkato", "count": merkato_count, "formatted": self._format_int(merkato_count)},
            {"key": "SK", "name": "Sklad",   "count": sklad_count,  "formatted": self._format_int(sklad_count)},
            {"key": "OF", "name": "Ofis",    "count": ofis_count,   "formatted": self._format_int(ofis_count)},
        ]

        shops_chart = [
            {"name": item["name"], "value": item["count"]}
            for item in shops_items
        ]

        # =========================
        # 2. ISHCHILAR
        # =========================
        employees_total = employees_qs.count()

        # =========================
        # 3. TERMINALLAR — cash_register_number vergul bilan ajratilgan
        # =========================
        cash_numbers_vat = tenants_qs.exclude(
            cash_register_number_vat__isnull=True
        ).exclude(
            cash_register_number_vat__exact=""
        ).values_list("cash_register_number_vat", flat=True)

        cash_numbers_turnover = tenants_qs.exclude(
            cash_register_number_turnover__isnull=True
        ).exclude(
            cash_register_number_turnover__exact=""
        ).values_list("cash_register_number_turnover", flat=True)

        terminals_total = sum(
            len([x for x in cn.split(",") if x.strip()])
            for cn in list(cash_numbers_vat) + list(cash_numbers_turnover)
        )

        # =========================
        # 4 & 5. SAVDO va SOLIQ TUSHUMLARI
        # =========================
        revenue_agg = tenants_qs.aggregate(
            okkm_vat=Coalesce(Sum(revenue_fields["okkm_vat"]), Decimal("0")),
            okkm_turnover=Coalesce(Sum(revenue_fields["okkm_turnover"]), Decimal("0")),
            e_payment_vat=Coalesce(Sum(revenue_fields["e_payment_vat"]), Decimal("0")),
            e_payment_turnover=Coalesce(Sum(revenue_fields["e_payment_turnover"]), Decimal("0")),
        )

        # SAVDO TUSHUMLARI: barcha savdo tushumlari (OKKM + elektron to'lov)
        sales_okkm = self._d(revenue_agg["okkm_vat"] + revenue_agg["okkm_turnover"])
        sales_e_payment = self._d(revenue_agg["e_payment_vat"] + revenue_agg["e_payment_turnover"])
        sales_total = sales_okkm + sales_e_payment

        # SOLIQ TUSHUMLARI: QQS 12% + Aylanmadan olinadigan soliq 1%
        QQS_RATE = Decimal("0.12")
        AOS_RATE = Decimal("0.01")
        vat_base = self._d(revenue_agg["okkm_vat"] + revenue_agg["e_payment_vat"])
        turnover_base = self._d(revenue_agg["okkm_turnover"] + revenue_agg["e_payment_turnover"])
        tax_from_vat = vat_base * QQS_RATE
        tax_from_turnover = turnover_base * AOS_RATE
        tax_revenue_total = tax_from_vat + tax_from_turnover

        # =========================
        # 6. KASSA APPARATLARI
        # =========================
        cash_registers_total = terminals_total

        # =========================
        # 7. TADBIRKORLIK SUBYEKTLARI
        # =========================
        mchj_count = tenants_qs.filter(business_type=ShopTenant.BusinessType.LEGAL).count()
        ytt_count = tenants_qs.filter(business_type=ShopTenant.BusinessType.YTT).count()
        other_count = tenants_qs.filter(business_type=ShopTenant.BusinessType.OTHER).count()
        business_total = tenants_qs.count()

        business_items = [
            {
                "key": "LEGAL",
                "name": "MCHJ",
                "count": mchj_count,
                "formatted": self._format_int(mchj_count),
            },
            {
                "key": "YTT",
                "name": "YTT",
                "count": ytt_count,
                "formatted": self._format_int(ytt_count),
            },
            {
                "key": "OTHER",
                "name": "Boshqa",
                "count": other_count,
                "formatted": self._format_int(other_count),
            },
        ]

        business_chart = [
            {"name": item["name"], "value": item["count"]}
            for item in business_items if item["count"] > 0
        ]

        response_data = {
            "period": period,
            "range": chart_range,
            "dashboard": {
                "shops": {
                    "title": "Do'konlar",
                    "count": total_shops,
                    "formatted": self._format_int(total_shops),
                    "items": shops_items,
                    "chart": shops_chart,
                },
                "employees": {
                    "title": "Ishchilar",
                    "label": "Nafar",
                    "count": employees_total,
                    "formatted": self._format_int(employees_total),
                },
                "terminals": {
                    "title": "Terminallar",
                    "count": terminals_total,
                    "formatted": self._format_int(terminals_total),
                },
                "tax_revenue": {
                    "title": "Soliq tushumlari",
                    "count": float(tax_revenue_total),
                    "formatted": f"{self._format_money_mln(tax_revenue_total)} mln so'm",
                    "chart": tax_chart,
                    "items": [
                        {
                            "key": "QQS",
                            "name": "QQS (12%)",
                            "count": float(tax_from_vat),
                            "formatted": f"{self._format_money_mln(tax_from_vat)} mln so'm",
                        },
                        {
                            "key": "AOS",
                            "name": "Aylanma soliq (1%)",
                            "count": float(tax_from_turnover),
                            "formatted": f"{self._format_money_mln(tax_from_turnover)} mln so'm",
                        },
                    ],
                },
                "sales_revenue": {
                    "title": "Savdo tushumlari",
                    "count": float(sales_total),
                    "formatted": f"{self._format_money_mln(sales_total)} mln so'm",
                    "chart": sales_chart,
                    "items": [
                        {
                            "key": "OKKM",
                            "name": "OKKM",
                            "count": float(sales_okkm),
                            "formatted": f"{self._format_money_mln(sales_okkm)} mln so'm",
                        },
                        {
                            "key": "E_PAYMENT",
                            "name": "Elektron to'lov",
                            "count": float(sales_e_payment),
                            "formatted": f"{self._format_money_mln(sales_e_payment)} mln so'm",
                        },
                    ],
                },
                "cash_registers": {
                    "title": "Kassa apparatlari",
                    "count": cash_registers_total,
                    "formatted": self._format_int(cash_registers_total),
                },
                "area": {
                    "title": "Savdo kompleks umumiy maydoni",
                    "total_kv": 48421,
                    "items": [
                        {"key": "A",  "name": "A blok",  "kv": 14012},
                        {"key": "B",  "name": "B blok",  "kv": 5533},
                        {"key": "J",  "name": "J blok",  "kv": 675},
                        {"key": "SM", "name": "Merkato", "kv": 1107},
                        {"key": "SK", "name": "Sklad",   "kv": 2400},
                    ],
                },
                "business_entities": {
                    "title": "Tadbirkorlik subyekti",
                    "count": business_total,
                    "formatted": self._format_int(business_total),
                    "items": business_items,
                    "chart": business_chart,
                },
            }
        }

        return Response(response_data)