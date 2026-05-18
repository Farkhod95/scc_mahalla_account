from decimal import Decimal

from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from monitoring.models import Shop, ShopTenant, TenantEmployee


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
        value = self._d(value)
        mln = value / Decimal("1000000")
        s = f"{mln:,.2f}".replace(",", " ")
        if s.endswith(".00"):
            s = s[:-3]
        return s

    def _get_period_fields(self, period):
        if period == "daily":
            return {"okkm": "dtd_okkm", "e_payment": "dtd_e_payment"}
        elif period == "monthly":
            return {"okkm": "mtd_okkm", "e_payment": "mtd_e_payment"}
        return {"okkm": "ytd_okkm", "e_payment": "ytd_e_payment"}

    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period", "yearly").lower()
        if period not in ["daily", "monthly", "yearly"]:
            period = "yearly"

        revenue_fields = self._get_period_fields(period)

        shops_qs = Shop.objects.all()
        tenants_qs = ShopTenant.objects.all()
        employees_qs = TenantEmployee.objects.all()

        area_agg = shops_qs.aggregate(
            total=Coalesce(Sum("total_area"), Decimal("0")),
            a=Coalesce(Sum("total_area", filter=Q(block_type=Shop.BlockType.BLOK_A)), Decimal("0")),
            b=Coalesce(Sum("total_area", filter=Q(block_type=Shop.BlockType.BLOK_B)), Decimal("0")),
            j=Coalesce(Sum("total_area", filter=Q(block_type=Shop.BlockType.BLOK_J)), Decimal("0")),
            merkato=Coalesce(Sum("total_area", filter=Q(block_type=Shop.BlockType.SAVDO_MARKAZ)), Decimal("0")),
            sklad=Coalesce(Sum("total_area", filter=Q(block_type=Shop.BlockType.SKLAD)), Decimal("0")),
            ofis=Coalesce(Sum("total_area", filter=Q(block_type=Shop.BlockType.OFIS)), Decimal("0")),
        )

        # =========================
        # 1. DO'KONLAR
        # =========================
        total_shops = shops_qs.count()

        a_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_A).count()
        b_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_B).count()
        j_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_J).count()
        merkato_count = shops_qs.filter(block_type=Shop.BlockType.SAVDO_MARKAZ).count()
        sklad_count = shops_qs.filter(block_type=Shop.BlockType.SKLAD).count()
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
        cash_numbers = tenants_qs.exclude(
            cash_register_number__isnull=True
        ).exclude(
            cash_register_number__exact=""
        ).values_list("cash_register_number", flat=True)

        terminals_total = sum(
            len([x for x in cn.split(",") if x.strip()])
            for cn in cash_numbers
        )

        # =========================
        # 4. SOLIQ TUSHUMLARI
        # Sizning modelda alohida soliq summasi yo'q.
        # Frontend kartani to'ldirish uchun vaqtincha savdo tushum totalini ishlatamiz.
        # Agar real soliq summasi bo'lsa, alohida field qo'shiladi.
        # =========================
        tax_revenue_agg = tenants_qs.aggregate(
            total=Coalesce(
                Sum(revenue_fields["okkm"]) + Sum(revenue_fields["e_payment"]),
                Decimal("0")
            )
        )
        tax_revenue_total = self._d(tax_revenue_agg["total"])

        # =========================
        # 5. SAVDO TUSHUMLARI
        # =========================
        sales_agg = tenants_qs.aggregate(
            okkm=Coalesce(Sum(revenue_fields["okkm"]), Decimal("0")),
            e_payment=Coalesce(Sum(revenue_fields["e_payment"]), Decimal("0")),
        )

        sales_okkm = self._d(sales_agg["okkm"])
        sales_e_payment = self._d(sales_agg["e_payment"])
        sales_total = sales_okkm + sales_e_payment

        # =========================
        # 6. KASSA APPARATLARI — terminallar bilan bir xil hisob
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
                },
                "sales_revenue": {
                    "title": "Savdo tushumlari",
                    "count": float(sales_total),
                    "formatted": f"{self._format_money_mln(sales_total)} mln so'm",
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
                    "total_kv": float(area_agg["total"]),
                    "items": [
                        {"key": "A",  "name": "A blok",  "kv": float(area_agg["a"])},
                        {"key": "B",  "name": "B blok",  "kv": float(area_agg["b"])},
                        {"key": "J",  "name": "J blok",  "kv": float(area_agg["j"])},
                        {"key": "SM", "name": "Merkato", "kv": float(area_agg["merkato"])},
                        {"key": "OF", "name": "Ofis",    "kv": float(area_agg["ofis"])},
                        {"key": "SK", "name": "Sklad",   "kv": float(area_agg["sklad"])},
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