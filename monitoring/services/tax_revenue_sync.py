"""
Soliq tushumi (company-account, payTax) sync — har faol ijarachi tin i uchun
belgilangan soliq kodlari bo'yicha kunlik/oylik/yillik payTax ni TaxRevenue ga yozadi.

Og'ir: har tin x 7 kod x 3 davr = 21 so'rov. Shu sababli faqat celery beat (tunda)
yoki management command orqali ishlaydi — request thread da EMAS. Dashboard endpoint
(reports/tax-revenue) tayyor TaxRevenue jadvalidan o'qiydi (jonli soliqqa bormaydi).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from django.db import transaction

from monitoring.models import ShopTenant, TaxRevenue
from monitoring.services import soliq_service
from monitoring.services.revenue_sync import _resolve_tin

logger = logging.getLogger(__name__)

# (taxCode, ko'rsatiladigan nom) — dashboard endpoint shu tartibda qaytaradi.
TAX_CODES = [
    (1, "QQS"),
    (32, "Foyda solig'i"),
    (36, "Ijtimoiy soliq"),
    (38, "Pensiya fondi badallari"),
    (46, "Jismoniy shaxs daromad solig'i"),
    (100, "Aylanma soliq"),
    (186, "Ijara daromad solig'i (NDFL)"),
]


@dataclass
class TaxRevenueSyncStats:
    tenants: int = 0
    skipped_inactive: int = 0
    with_tin: int = 0
    rows_written: int = 0
    cleared: int = 0
    errors: int = 0


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(0)


def _pay_tax(tin: str, tax_code: int, period_from: str, period_to: str, stats) -> Optional[Decimal]:
    """Bitta kod + davr uchun payTax. Xato bo'lsa None (chaqiruvchi eski qiymatni saqlaydi)."""
    try:
        data = soliq_service.get_company_account(tin, period_from, period_to, tax_code) or {}
    except (soliq_service.SoliqError, requests.RequestException) as e:
        logger.warning(
            "tax sync xato (tin=%s, kod=%s, %s..%s): %s",
            tin, tax_code, period_from, period_to, e,
        )
        stats.errors += 1
        return None
    return _to_decimal(data.get("payTax"))


def sync_tax_revenue() -> TaxRevenueSyncStats:
    """
    Har faol ijarachi tin i uchun TAX_CODES bo'yicha dtd/mtd/ytd payTax ni
    TaxRevenue ga upsert qiladi. Faol bo'lmagan (stale) tin lar jadvaldan o'chiriladi.
    """
    today = date.today()
    ytd_from = f"01.01.{today.year}"
    mtd_from = today.strftime("01.%m.%Y")
    today_str = today.strftime("%d.%m.%Y")

    stats = TaxRevenueSyncStats()

    # 1) Faol ijarachilarning tin lari (takrorsiz).
    active_tins: set[str] = set()
    for tenant in ShopTenant.objects.all().iterator():
        stats.tenants += 1
        if tenant.activity_status == ShopTenant.ActivityStatus.INACTIVE:
            stats.skipped_inactive += 1
            continue
        tin = _resolve_tin(tenant)
        if tin:
            active_tins.add(tin)
    stats.with_tin = len(active_tins)

    # 2) Har tin x har kod: 3 davr payTax -> upsert. Davrlardan biri xato bo'lsa
    #    shu (tin, kod) bu safar yangilanmaydi (eski qiymat saqlanadi).
    for tin in active_tins:
        for code, _name in TAX_CODES:
            ytd = _pay_tax(tin, code, ytd_from, today_str, stats)
            mtd = _pay_tax(tin, code, mtd_from, today_str, stats)
            dtd = _pay_tax(tin, code, today_str, today_str, stats)
            if ytd is None or mtd is None or dtd is None:
                continue
            with transaction.atomic():
                TaxRevenue.objects.update_or_create(
                    tin=tin,
                    tax_code=code,
                    defaults={"dtd_pay": dtd, "mtd_pay": mtd, "ytd_pay": ytd},
                )
            stats.rows_written += 1

    # 3) Hech qaysi tenant'ga (faol YOKI nofaol) tegishli bo'lmagan orphan tin larni
    #    tozalaymiz. Nofaol tenantlar uchun qo'lda backfill qilingan tax (stir/PINFL
    #    bo'yicha) SAQLANADI — ular ketgan, lekin tarixiy tushumi kerak. active_tins
    #    bo'sh bo'lsa (soliq ishlamadi) — tozalamaymiz.
    if active_tins:
        keep = set(active_tins)
        for stir, pinfl in ShopTenant.objects.values_list("stir", "leader_jshshir"):
            if stir and stir.strip():
                keep.add(stir.strip())
            if pinfl and pinfl.strip():
                keep.add(pinfl.strip())
        deleted, _ = TaxRevenue.objects.exclude(tin__in=keep).delete()
        stats.cleared = deleted

    return stats
