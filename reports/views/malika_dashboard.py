from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Q
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
    1:1 response for the dashboard.

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

    @staticmethod
    def _count_distinct_pinfl(qs):
        """
        Tadbirkorlar sonini pinfl (leader_jshshir) bo'yicha UNIKAL hisoblaydi:
        bitta YTT/MCHJ bir nechta do'kondan joy olsa ham 1 marta sanaladi.
        pinfl bo'sh/yo'q qatorlar alohida sanaladi (ularni birlashtirib bo'lmaydi).
        """
        with_pinfl = (
            qs.exclude(leader_jshshir__isnull=True)
              .exclude(leader_jshshir="")
              .values("leader_jshshir")
              .distinct()
              .count()
        )
        without_pinfl = qs.filter(
            Q(leader_jshshir__isnull=True) | Q(leader_jshshir="")
        ).count()
        return with_pinfl + without_pinfl

    def _format_money_mln(self, value):
        # Values are stored in millions of so'm in the DB
        # (e.g. 2230.9 = 2 230 900 000 so'm)
        value = self._d(value)
        s = f"{value:,.2f}".replace(",", " ")
        if s.endswith(".00"):
            s = s[:-3]
        return s

    # =========================
    # REVENUE CHART (from FacturaRevenueDaily, in millions of so'm)
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

        # Chart granularity derives from the period (day->week, month->months, year->years).
        # Optionally it can be controlled separately via ?range=.
        chart_range = request.query_params.get("range", "").lower()
        if chart_range not in ["week", "month", "year"]:
            chart_range = {"daily": "week", "monthly": "month", "yearly": "year"}.get(period, "week")

        sales_chart, tax_chart = self._revenue_charts(chart_range, date.today())

        shops_qs = Shop.objects.all()
        # Nofaol (INACTIVE) ijarachilar dashboard hisob-kitobiga kirmaydi —
        # tadbirkor soni, terminal, OKKM tushum, cheklar va xodimlar shulardan.
        tenants_qs = ShopTenant.objects.exclude(
            activity_status=ShopTenant.ActivityStatus.INACTIVE
        )
        employees_qs = TenantEmployee.objects.exclude(
            tenant__activity_status=ShopTenant.ActivityStatus.INACTIVE
        )

        # =========================
        # 1. SHOPS
        # =========================
        total_shops = shops_qs.count()

        a_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_A).count()
        b_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_B).count()
        j_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_J).count()
        merkato_count = max(shops_qs.filter(block_type=Shop.BlockType.SAVDO_MARKAZ).count(), 78)
        sklad_count = max(shops_qs.filter(block_type=Shop.BlockType.SKLAD).count(), 74)

        shops_items = [
            {"key": "A",  "name": "A blok",  "count": a_count,      "formatted": self._format_int(a_count)},
            {"key": "B",  "name": "B blok",  "count": b_count,      "formatted": self._format_int(b_count)},
            {"key": "J",  "name": "J blok",  "count": j_count,      "formatted": self._format_int(j_count)},
            {"key": "SM", "name": "Merkato savdo markazi", "count": merkato_count, "formatted": self._format_int(merkato_count)},
            {"key": "SK", "name": "Ombor",   "count": sklad_count,  "formatted": self._format_int(sklad_count)},
        ]

        shops_chart = [
            {"name": item["name"], "value": item["count"]}
            for item in shops_items
        ]

        # =========================
        # 2. EMPLOYEES
        # =========================
        employees_total = employees_qs.count()

        # =========================
        # 3. TERMINALS — cash_register_number is comma-separated
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
        # 4 & 5. SALES and TAX REVENUE
        # =========================
        # Elektron to'lov (faktura) — grafik bilan bir manba (FacturaRevenueDaily),
        # mln so'm da. Card "Total" = grafik davri yig'indisi.
        sales_e_payment = self._d(sum(item["value"] for item in sales_chart))
        tax_revenue_total = self._d(sum(item["value"] for item in tax_chart))

        # OKKM (NKM cheklar) tushumi — celery beat sync qilgan DB maydonlaridan,
        # tanlangan davrga mos ustun (yearly->ytd, monthly->mtd, daily->dtd).
        okkm_prefix = {"yearly": "ytd", "monthly": "mtd", "daily": "dtd"}.get(period, "ytd")
        okkm_agg = tenants_qs.aggregate(
            v=Sum(f"{okkm_prefix}_okkm_vat"),
            t=Sum(f"{okkm_prefix}_okkm_turnover"),
        )
        sales_okkm = ((self._d(okkm_agg["v"]) + self._d(okkm_agg["t"])) / MLN).quantize(Decimal("0.01"))

        # Umumiy savdo tushumi = elektron to'lov + OKKM.
        sales_total = sales_e_payment + sales_okkm

        # Cheklar soni — oylik/kunlik davr uchun saqlangan (yillik maydon yo'q).
        checks_field = {"monthly": "monthly_checks_count", "daily": "daily_checks_count"}.get(period)
        if checks_field:
            c_agg = tenants_qs.aggregate(
                v=Sum(f"{checks_field}_vat"),
                t=Sum(f"{checks_field}_turnover"),
            )
            cheque_count_total = int(self._d(c_agg["v"]) + self._d(c_agg["t"]))
        else:
            cheque_count_total = None

        # Factura vatSum = VAT. Turnover tax requires a separate source.
        tax_from_vat = tax_revenue_total
        tax_from_turnover = Decimal("0")

        # =========================
        # 6. CASH REGISTERS
        # =========================
        cash_registers_total = terminals_total

        # =========================
        # 7. BUSINESS ENTITIES
        # =========================
        # pinfl (leader_jshshir) bo'yicha unikal — bitta tadbirkor bir nechta
        # do'kondan joy olsa ham 1 marta sanaladi.
        mchj_count = self._count_distinct_pinfl(tenants_qs.filter(business_type=ShopTenant.BusinessType.LEGAL))
        ytt_count = self._count_distinct_pinfl(tenants_qs.filter(business_type=ShopTenant.BusinessType.YTT))
        other_count = self._count_distinct_pinfl(tenants_qs.filter(business_type=ShopTenant.BusinessType.OTHER))
        business_total = self._count_distinct_pinfl(tenants_qs)

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
                    "cheque_count": cheque_count_total,
                    "cheque_count_formatted": (
                        self._format_int(cheque_count_total) if cheque_count_total is not None else None
                    ),
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
                        {"key": "SM", "name": "Merkato savdo markazi", "kv": 1107},
                        {"key": "SK", "name": "Ombor",   "kv": 2400},
                        {"key": "PARKING", "name": "Avtoturargoh", "kv": 14965},
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
