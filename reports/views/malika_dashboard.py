from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from monitoring.models import (
    Shop, ShopTenant, TenantEmployee, FacturaRevenueDaily, OkkmRevenueDaily,
    TaxRevenue,
)

WEEKDAY_LABELS = ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"]  # Mon..Sun
MONTH_LABELS = ["Yan", "Fev", "Mar", "Apr", "May", "Iyn",
                "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"]

# Soliq kodlari (TaxRevenue.tax_code) — dashboardda ko'rsatiladiganlar.
TAX_CODE_QQS = 1
TAX_CODE_FOYDA = 32
TAX_CODE_AYLANMA = 100
TAX_CODE_NDFL = 46          # Jismoniy shaxs daromad solig'i (ishchilar yonida)

# Kunlik soliq o'zimiz hisoblanadi (soliq ma'lumoti kech keladi): savdoga nisbatan.
DAILY_TAX_RATE_YTT = Decimal("0.01")    # YTT  -> 1%
DAILY_TAX_RATE_MCHJ = Decimal("0.04")   # MCHJ / boshqa -> 4%


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

    # =========================
    # REVENUE CHART (FacturaRevenueDaily + OkkmRevenueDaily, in raw so'm)
    # =========================
    def _chart_value(self, value):
        # Xom so'm (to'liq summa), float — front o'zi mln/mlrd qilib formatlaydi.
        return round(float(value or 0), 2)

    def _chart_sum_by_date(self, start, end):
        """
        Kunlik (sales, tax, okkm_sales) — faktura va OKKM birga, xom so'm.
          sales      = faktura savdo + OKKM turnover (grafik ustuni: jami savdo)
          tax        = faktura QQS + OKKM QQS (chek vat) — jami soliq ustuni
          okkm_sales = OKKM turnover (karta "OKKM"/"Elektron to'lov" ni ajratish uchun)
        """
        out: dict = {}
        for r in (
            FacturaRevenueDaily.objects
            .filter(date__gte=start, date__lte=end)
            .values("date")
            .annotate(s=Sum("sales"), t=Sum("tax"))
        ):
            out[r["date"]] = [r["s"] or 0, r["t"] or 0, 0]

        for r in (
            OkkmRevenueDaily.objects
            .filter(date__gte=start, date__lte=end)
            .values("date")
            .annotate(o=Sum("turnover"), v=Sum("vat"))
        ):
            okkm = r["o"] or 0
            okkm_vat = r["v"] or 0
            bucket = out.setdefault(r["date"], [0, 0, 0])
            bucket[0] += okkm       # jami savdo ustuniga
            bucket[1] += okkm_vat   # soliq (QQS) ustuniga
            bucket[2] += okkm       # OKKM savdo ulushi (karta uchun)
        return out

    def _revenue_charts(self, rng, today):
        """
        (sales_chart, tax_chart, okkm_total) — rng: week|month|year.
        sales_chart har ustuni faktura+OKKM (kunlik tarixdan); okkm_total — shu
        oynadagi OKKM ulushi (karta jami = grafik yig'indisi invariantini saqlash uchun).
        """
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
            buckets = {k: [Decimal(0), Decimal(0), Decimal(0)] for k in keys}
            for d, (s, t, o) in by_date.items():
                k = (d.year, d.month)
                if k in buckets:
                    buckets[k][0] += Decimal(s); buckets[k][1] += Decimal(t); buckets[k][2] += Decimal(o)
            order = keys
            label_of = dict(zip(keys, labels))
        elif rng == "year":
            years = [today.year - i for i in range(6, -1, -1)]
            start = date(years[0], 1, 1)
            by_date = self._chart_sum_by_date(start, today)
            buckets = {y: [Decimal(0), Decimal(0), Decimal(0)] for y in years}
            for d, (s, t, o) in by_date.items():
                if d.year in buckets:
                    buckets[d.year][0] += Decimal(s); buckets[d.year][1] += Decimal(t); buckets[d.year][2] += Decimal(o)
            order = years
            label_of = {y: str(y) for y in years}
        else:  # week
            monday = today - timedelta(days=today.weekday())
            days = [monday + timedelta(days=i) for i in range(7)]
            by_date = self._chart_sum_by_date(days[0], days[-1])
            buckets = {d: list(by_date.get(d, (0, 0, 0))) for d in days}
            order = days
            label_of = {d: WEEKDAY_LABELS[i] for i, d in enumerate(days)}

        sales = [{"label": label_of[k], "value": self._chart_value(buckets[k][0])} for k in order]
        tax = [{"label": label_of[k], "value": self._chart_value(buckets[k][1])} for k in order]
        okkm_total = sum((self._d(buckets[k][2]) for k in order), Decimal(0))
        return sales, tax, okkm_total

    # =========================
    # TAX REVENUE (TaxRevenue jadvalidan — integratsiyadan saqlangan, jonli emas)
    # =========================
    def _tax_by_code(self, period):
        """
        {tax_code: Decimal} — TaxRevenue dan tanlangan davr (monthly->mtd, yearly->ytd)
        bo'yicha barcha tin lar yig'indisi. daily uchun ishlatilmaydi (o'zimiz hisoblaymiz).
        """
        field = {"monthly": "mtd_pay", "yearly": "ytd_pay"}.get(period)
        if not field:
            return {}
        out = {}
        for r in TaxRevenue.objects.values("tax_code").annotate(s=Sum(field)):
            out[r["tax_code"]] = self._d(r["s"])
        return out

    def _daily_computed_tax(self, today):
        """
        Kunlik soliq — soliq ma'lumoti kech kelgani uchun o'zimiz savdodan hisoblaymiz:
        MCHJ kunlik savdo x 4% + YTT kunlik savdo x 1%.

        Savdo = bugungi FacturaRevenueDaily.sales + OkkmRevenueDaily.turnover, kalit
        (seller_tin/tin) tenant turiga (business_type) bog'lanadi. Kalit topilmasa:
        14 xonali -> PINFL (YTT 1%), aks holda -> MCHJ 4%.
        """
        sales = defaultdict(Decimal)
        for r in (FacturaRevenueDaily.objects.filter(date=today)
                  .values("seller_tin").annotate(s=Sum("sales"))):
            key = (r["seller_tin"] or "").strip()
            if key:
                sales[key] += self._d(r["s"])
        for r in (OkkmRevenueDaily.objects.filter(date=today)
                  .values("tin").annotate(o=Sum("turnover"))):
            key = (r["tin"] or "").strip()
            if key:
                sales[key] += self._d(r["o"])

        if not sales:
            return Decimal("0")

        # kalit (STIR yoki PINFL) -> business_type
        stir_type, pinfl_type = {}, {}
        for t in (ShopTenant.objects
                  .exclude(activity_status=ShopTenant.ActivityStatus.INACTIVE)
                  .values("stir", "leader_jshshir", "business_type")):
            s = (t["stir"] or "").strip()
            p = (t["leader_jshshir"] or "").strip()
            if s:
                stir_type[s] = t["business_type"]
            if p:
                pinfl_type[p] = t["business_type"]

        total = Decimal("0")
        for key, amount in sales.items():
            btype = stir_type.get(key) or pinfl_type.get(key)
            if btype is None:
                btype = ShopTenant.BusinessType.YTT if len(key) == 14 else ShopTenant.BusinessType.LEGAL
            rate = DAILY_TAX_RATE_YTT if btype == ShopTenant.BusinessType.YTT else DAILY_TAX_RATE_MCHJ
            total += amount * rate
        return total

    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period", "yearly").lower()
        if period not in ["daily", "monthly", "yearly"]:
            period = "yearly"

        # Chart granularity derives from the period (day->week, month->months, year->years).
        # Optionally it can be controlled separately via ?range=.
        chart_range = request.query_params.get("range", "").lower()
        if chart_range not in ["week", "month", "year"]:
            chart_range = {"daily": "week", "monthly": "month", "yearly": "year"}.get(period, "week")

        sales_chart, tax_chart, sales_okkm = self._revenue_charts(chart_range, date.today())

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
        g_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_G).count()
        j_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_J).count()
        merkato_count = max(shops_qs.filter(block_type=Shop.BlockType.SAVDO_MARKAZ).count(), 78)
        sklad_count = max(shops_qs.filter(block_type=Shop.BlockType.SKLAD).count(), 74)

        shops_items = [
            {"key": "A",  "name": "A blok",  "count": a_count},
            {"key": "B",  "name": "B blok",  "count": b_count},
            {"key": "G",  "name": "G blok",  "count": g_count},
            {"key": "J",  "name": "J blok",  "count": j_count},
            {"key": "SM", "name": "Merkato savdo markazi", "count": merkato_count},
            {"key": "SK", "name": "Ombor",   "count": sklad_count},
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
        # Savdo grafigi = faktura (FacturaRevenueDaily) + OKKM (OkkmRevenueDaily),
        # ikkalasi ham kunlik tarixdan kun-bekun yig'iladi (_revenue_charts). Karta
        # jami = grafik yig'indisi, OKKM/elektron to'lov ulushi ham shu oynadan —
        # hammasi bir manba, bir davr (invariant: items yig'indisi = count).
        sales_total = self._d(sum(item["value"] for item in sales_chart))
        sales_okkm = self._d(sales_okkm)                    # grafik oynasidagi OKKM ulushi
        sales_e_payment = sales_total - sales_okkm          # qolgani — elektron to'lov (faktura)

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

        # =========================
        # SOLIQ TUSHUMLARI
        #   - oylik/yillik: TaxRevenue jadvalidan (integratsiyadan saqlangan) —
        #     QQS(1) + Foyda(32) + Aylanma(100). NDFL(46) ishchilar yonida.
        #   - kunlik: o'zimiz savdodan hisoblaymiz (MCHJ 4% + YTT 1%), bitta umumiy son.
        # =========================
        if period == "daily":
            tax_total = self._daily_computed_tax(date.today())
            tax_items = []                  # kunlik — bitta umumiy son, breakdown yo'q
            income_tax_value = None         # NDFL faqat oylik/yillik
        else:
            by_code = self._tax_by_code(period)
            qqs = by_code.get(TAX_CODE_QQS, Decimal("0"))
            foyda = by_code.get(TAX_CODE_FOYDA, Decimal("0"))
            aylanma = by_code.get(TAX_CODE_AYLANMA, Decimal("0"))
            tax_total = qqs + foyda + aylanma
            tax_items = [
                {"key": "QQS", "name": "QQS", "count": float(qqs)},
                {"key": "FOYDA", "name": "Foyda solig'i", "count": float(foyda)},
                {"key": "AYLANMA", "name": "Aylanma soliq", "count": float(aylanma)},
            ]
            income_tax_value = float(by_code.get(TAX_CODE_NDFL, Decimal("0")))

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
            {"key": "LEGAL", "name": "MCHJ",   "count": mchj_count},
            {"key": "YTT",   "name": "YTT",    "count": ytt_count},
            {"key": "OTHER", "name": "Boshqa", "count": other_count},
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
                    "items": shops_items,
                    "chart": shops_chart,
                },
                "employees": {
                    "title": "Ishchilar",
                    "label": "Nafar",
                    "count": employees_total,
                    "income_tax": {
                        "name": "Jismoniy shaxs daromad solig'i",
                        "count": income_tax_value,   # oylik/yillik qiymat, kunlikda null
                    },
                },
                "terminals": {
                    "title": "Terminallar",
                    "count": terminals_total,
                },
                "tax_revenue": {
                    "title": "Soliq tushumlari",
                    "count": float(tax_total),
                    "chart": tax_chart,
                    "items": tax_items,
                },
                "sales_revenue": {
                    "title": "Savdo tushumlari",
                    "count": float(sales_total),
                    "cheque_count": cheque_count_total,
                    "chart": sales_chart,
                    "items": [
                        {
                            "key": "OKKM",
                            "name": "OKKM",
                            "count": float(sales_okkm),
                        },
                        {
                            "key": "E_PAYMENT",
                            "name": "Elektron to'lov",
                            "count": float(sales_e_payment),
                        },
                    ],
                },
                "cash_registers": {
                    "title": "Kassa apparatlari",
                    "count": cash_registers_total,
                },
                "area": {
                    "title": "Savdo kompleks umumiy maydoni",
                    "total_kv": 48421,
                    "items": [
                        {"key": "A",  "name": "A blok",  "kv": 23741},
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
                    "items": business_items,
                    "chart": business_chart,
                },
            }
        }

        return Response(response_data)
