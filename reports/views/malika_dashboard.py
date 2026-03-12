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

    def _get_period_fields(self, period):
        if period == "daily":
            return {
                "okkm": "dtd_okkm",
                "e_invoice": "dtd_e_invoice",
                "qr": "dtd_qr",
            }
        elif period == "monthly":
            return {
                "okkm": "mtd_okkm",
                "e_invoice": "mtd_e_invoice",
                "qr": "mtd_qr",
            }
        return {
            "okkm": "ytd_okkm",
            "e_invoice": "ytd_e_invoice",
            "qr": "ytd_qr",
        }

    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period", "yearly").lower()
        if period not in ["daily", "monthly", "yearly"]:
            period = "yearly"

        revenue_fields = self._get_period_fields(period)

        shops_qs = Shop.objects.filter(is_delete=False)
        tenants_qs = ShopTenant.objects.filter(is_delete=False)
        employees_qs = TenantEmployee.objects.filter(is_delete=False)

        # =========================
        # 1. DO'KONLAR
        # =========================
        total_shops = shops_qs.count()

        a_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_A).count()
        b_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_B).count()
        j_count = shops_qs.filter(block_type=Shop.BlockType.BLOK_J).count()
        merkalo_count = shops_qs.filter(block_type=Shop.BlockType.SAVDO_MARKAZ).count()

        # Sizning modelda OFFICE va SKLAD yo'q.
        # Hozircha 0 qaytaryapmiz.
        office_count = 0
        sklad_count = 0

        shops_items = [
            {
                "key": "A",
                "name": "A blok",
                "count": a_count,
                "formatted": self._format_int(a_count),
            },
            {
                "key": "B",
                "name": "B blok",
                "count": b_count,
                "formatted": self._format_int(b_count),
            },
            {
                "key": "J",
                "name": "J blok",
                "count": j_count,
                "formatted": self._format_int(j_count),
            },
            {
                "key": "SM",
                "name": 'TЦ "Merkalo"',
                "count": merkalo_count,
                "formatted": self._format_int(merkalo_count),
            },
            {
                "key": "OFFICE",
                "name": "Ofis",
                "count": office_count,
                "formatted": self._format_int(office_count),
            },
            {
                "key": "SKLAD",
                "name": "Sklad",
                "count": sklad_count,
                "formatted": self._format_int(sklad_count),
            },
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
        # 3. TERMINALLAR
        # Screenshotdagi terminal soni uchun sizda alohida model yo'q.
        # cash_register_number bo'sh bo'lmagan tenantlarni terminal deb olyapmiz.
        # =========================
        terminals_total = tenants_qs.exclude(
            cash_register_number__isnull=True
        ).exclude(
            cash_register_number__exact=""
        ).count()

        # =========================
        # 4. SOLIQ TUSHUMLARI
        # Sizning modelda alohida soliq summasi yo'q.
        # Frontend kartani to'ldirish uchun vaqtincha savdo tushum totalini ishlatamiz.
        # Agar real soliq summasi bo'lsa, alohida field qo'shiladi.
        # =========================
        tax_revenue_agg = tenants_qs.aggregate(
            total=Coalesce(
                Sum(revenue_fields["okkm"]) +
                Sum(revenue_fields["e_invoice"]) +
                Sum(revenue_fields["qr"]),
                Decimal("0")
            )
        )
        tax_revenue_total = self._d(tax_revenue_agg["total"])

        # =========================
        # 5. SAVDO TUSHUMLARI
        # =========================
        sales_agg = tenants_qs.aggregate(
            okkm=Coalesce(Sum(revenue_fields["okkm"]), Decimal("0")),
            e_invoice=Coalesce(Sum(revenue_fields["e_invoice"]), Decimal("0")),
            qr=Coalesce(Sum(revenue_fields["qr"]), Decimal("0")),
        )

        sales_okkm = self._d(sales_agg["okkm"])
        sales_e_invoice = self._d(sales_agg["e_invoice"])
        sales_qr = self._d(sales_agg["qr"])
        sales_total = sales_okkm + sales_e_invoice + sales_qr

        # =========================
        # 6. KASSA APPARATLARI
        # distinct cash_register_number
        # =========================
        cash_registers_total = tenants_qs.exclude(
            cash_register_number__isnull=True
        ).exclude(
            cash_register_number__exact=""
        ).values("cash_register_number").distinct().count()

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
                    "formatted": f"{self._format_money(tax_revenue_total)} so'm",
                },
                "sales_revenue": {
                    "title": "Savdo tushumlari",
                    "count": float(sales_total),
                    "formatted": f"{self._format_money(sales_total)} so'm",
                    "items": [
                        {
                            "key": "OKKM",
                            "name": "OKKM",
                            "count": float(sales_okkm),
                            "formatted": self._format_money(sales_okkm),
                        },
                        {
                            "key": "E_INVOICE",
                            "name": "EHF",
                            "count": float(sales_e_invoice),
                            "formatted": self._format_money(sales_e_invoice),
                        },
                        {
                            "key": "QR",
                            "name": "QR",
                            "count": float(sales_qr),
                            "formatted": self._format_money(sales_qr),
                        },
                    ],
                },
                "cash_registers": {
                    "title": "Kassa apparatlari",
                    "count": cash_registers_total,
                    "formatted": self._format_int(cash_registers_total),
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