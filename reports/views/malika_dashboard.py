from decimal import Decimal

from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from monitoring.models import Shop, ShopTenant, TenantEmployee, ShopCamera


class MalikaDashboardReportView(APIView):
    """
    Dashboard API

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

    def _money(self, value):
        value = self._d(value)
        return float(value)

    def get_revenue_fields(self, period: str):
        """
        period bo'yicha fieldlar
        """
        if period == "daily":
            return "dtd_okkm", "dtd_e_invoice", "dtd_qr"
        elif period == "monthly":
            return "mtd_okkm", "mtd_e_invoice", "mtd_qr"
        return "ytd_okkm", "ytd_e_invoice", "ytd_qr"

    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period", "yearly").lower()
        if period not in ["daily", "monthly", "yearly"]:
            period = "yearly"

        okkm_field, einvoice_field, qr_field = self.get_revenue_fields(period)

        # -----------------------------
        # 1. Shop statistikasi
        # -----------------------------
        shops_qs = Shop.objects.filter(is_delete=False)

        total_shops = shops_qs.count()

        shop_block_counts = shops_qs.values("block_type").annotate(
            count=Count("id")
        ).order_by("block_type")

        block_map = {
            Shop.BlockType.BLOK_A: "A blok",
            Shop.BlockType.BLOK_B: "B blok",
            Shop.BlockType.BLOK_J: "J blok",
            Shop.BlockType.SAVDO_MARKAZ: "Savdo markazi",
            Shop.BlockType.PARKOVKA: "Avtoturargoh",
        }

        blocks = []
        for item in shop_block_counts:
            code = item["block_type"]
            blocks.append({
                "code": code,
                "name": block_map.get(code, code),
                "count": item["count"],
            })

        # -----------------------------
        # 2. Tenant statistikasi
        # -----------------------------
        tenants_qs = ShopTenant.objects.filter(is_delete=False)

        total_tenants = tenants_qs.count()

        tenant_type_counts = tenants_qs.values("business_type").annotate(
            count=Count("id")
        ).order_by("business_type")

        business_type_map = {
            ShopTenant.BusinessType.YTT: "YTT",
            ShopTenant.BusinessType.LEGAL: "MCHJ",
            ShopTenant.BusinessType.OTHER: "Boshqa",
        }

        tenant_types = []
        for item in tenant_type_counts:
            code = item["business_type"]
            tenant_types.append({
                "code": code,
                "name": business_type_map.get(code, code or "Noma'lum"),
                "count": item["count"],
            })

        # -----------------------------
        # 3. Xodimlar statistikasi
        # -----------------------------
        employees_qs = TenantEmployee.objects.filter(is_delete=False)
        total_employees = employees_qs.count()

        declared_employees_count = tenants_qs.aggregate(
            total=Coalesce(Sum("employees_count"), 0)
        )["total"] or 0

        # -----------------------------
        # 4. Kameralar / terminallar / kassa
        # -----------------------------
        total_cameras = ShopCamera.objects.filter(is_delete=False).count()

        total_terminals = tenants_qs.exclude(
            cash_register_number__isnull=True
        ).exclude(
            cash_register_number__exact=""
        ).count()

        total_cash_registers = tenants_qs.exclude(
            cash_register_number__isnull=True
        ).exclude(
            cash_register_number__exact=""
        ).values("cash_register_number").distinct().count()

        # -----------------------------
        # 5. Savdo tushumlari
        # -----------------------------
        revenue_agg = tenants_qs.aggregate(
            okkm=Coalesce(Sum(okkm_field), Decimal("0")),
            e_invoice=Coalesce(Sum(einvoice_field), Decimal("0")),
            qr=Coalesce(Sum(qr_field), Decimal("0")),
        )

        total_sales_revenue = (
            self._d(revenue_agg["okkm"]) +
            self._d(revenue_agg["e_invoice"]) +
            self._d(revenue_agg["qr"])
        )

        # -----------------------------
        # 6. Soliq tushumlari
        # Eslatma:
        # modelda alohida soliq summasi yo'q.
        # Shu sababli hozircha tax_type bo'yicha count qaytaryapmiz.
        # Agar keyin soliq_summasi field qo'shilsa, summaga o'tkazamiz.
        # -----------------------------
        tax_type_counts = tenants_qs.values("tax_type").annotate(
            count=Count("id")
        ).order_by("tax_type")

        tax_type_map = {
            ShopTenant.TaxType.VAT: "QQS",
            ShopTenant.TaxType.MONTHLY_INCOME: "Oylik daromad solig'i",
            ShopTenant.TaxType.OTHER: "Boshqa",
        }

        tax_types = []
        for item in tax_type_counts:
            code = item["tax_type"]
            tax_types.append({
                "code": code,
                "name": tax_type_map.get(code, code or "Noma'lum"),
                "count": item["count"],
            })

        # -----------------------------
        # 7. Qizil toifa
        # -----------------------------
        red_category_count = tenants_qs.filter(is_red_category=True).count()

        # -----------------------------
        # 8. Yong'in xavfsizligi
        # -----------------------------
        fire_level_counts = tenants_qs.values("fire_safety_level").annotate(
            count=Count("id")
        ).order_by("fire_safety_level")

        fire_level_map = {
            ShopTenant.FireSafetyLevel.LOW: "Past",
            ShopTenant.FireSafetyLevel.MEDIUM: "O'rtacha",
            ShopTenant.FireSafetyLevel.HIGH: "Yuqori",
        }

        fire_levels = []
        for item in fire_level_counts:
            code = item["fire_safety_level"]
            fire_levels.append({
                "code": code,
                "name": fire_level_map.get(code, code or "Noma'lum"),
                "count": item["count"],
            })

        fire_alarm_count = tenants_qs.filter(has_fire_alarm=True).count()

        # -----------------------------
        # 9. Tashrif va chek statistikasi
        # -----------------------------
        if period == "daily":
            visitors_total = tenants_qs.aggregate(
                total=Coalesce(Sum("daily_visitors"), 0)
            )["total"] or 0
            checks_total = tenants_qs.aggregate(
                total=Coalesce(Sum("daily_checks_count"), 0)
            )["total"] or 0
        elif period == "monthly":
            visitors_total = tenants_qs.aggregate(
                total=Coalesce(Sum("monthly_visitors"), 0)
            )["total"] or 0
            checks_total = tenants_qs.aggregate(
                total=Coalesce(Sum("monthly_checks_count"), 0)
            )["total"] or 0
        else:
            visitors_total = tenants_qs.aggregate(
                total=Coalesce(Sum("monthly_visitors"), 0)
            )["total"] or 0
            checks_total = tenants_qs.aggregate(
                total=Coalesce(Sum("monthly_checks_count"), 0)
            )["total"] or 0

        data = {
            "period": period,

            "summary": {
                "total_shops": total_shops,
                "total_tenants": total_tenants,
                "total_employees": total_employees,
                "declared_employees_count": declared_employees_count,
                "total_cameras": total_cameras,
                "total_terminals": total_terminals,
                "total_cash_registers": total_cash_registers,
                "red_category_count": red_category_count,
                "visitors_total": visitors_total,
                "checks_total": checks_total,
            },

            "shop_statistics": {
                "total": total_shops,
                "blocks": blocks,
            },

            "tenant_statistics": {
                "total": total_tenants,
                "business_types": tenant_types,
            },

            "employee_statistics": {
                "actual_employee_records": total_employees,
                "declared_employee_count": declared_employees_count,
            },

            "equipment_statistics": {
                "cameras": total_cameras,
                "terminals": total_terminals,
                "cash_registers": total_cash_registers,
            },

            "sales_revenue": {
                "period": period,
                "okkm": self._money(revenue_agg["okkm"]),
                "e_invoice": self._money(revenue_agg["e_invoice"]),
                "qr": self._money(revenue_agg["qr"]),
                "total": self._money(total_sales_revenue),
            },

            "tax_statistics": {
                "types": tax_types,
            },

            "fire_safety_statistics": {
                "levels": fire_levels,
                "has_fire_alarm_count": fire_alarm_count,
            },
        }

        return Response(data)