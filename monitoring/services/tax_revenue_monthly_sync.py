"""
Soliq tushumi (company-account payTax) — OYLIK TARIXni TaxRevenueMonthly ga yig'adi.

Har faol ijarachi tin i uchun belgilangan kodlar bo'yicha HAR OY (period = oy
boshidan oy oxirigacha; joriy oy bugungacha) payTax ni so'rab upsert qiladi.
O'tgan oylar o'zgarmaydi, shuning uchun kunlik (celery) sync faqat JORIY oyni
yangilaydi (--only-current); to'liq yil bir marta backfill qilinadi.

Dashboard (oylik/yillik) va reports/tax-revenue (oy filteri) SHU jadvaldan o'qiydi.

DIQQAT: soliqqa boradi — soliq API ochiladigan SERVERDA ishlating. Og'ir:
har tin x kod x oy = 1 so'rov.
"""
from __future__ import annotations

import calendar
import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from django.db import transaction

from monitoring.models import ShopTenant, TaxRevenueMonthly
from monitoring.services import soliq_service
from monitoring.services.revenue_sync import _resolve_tin

logger = logging.getLogger(__name__)

# Dashboard + reports/tax-revenue ishlatadigan kodlar (QQS, Foyda, NDFL, Aylanma).
MONTHLY_TAX_CODES = [
    (1, "QQS"),
    (32, "Foyda solig'i"),
    (46, "Jismoniy shaxs daromad solig'i"),
    (100, "Aylanma soliq"),
]


@dataclass
class TaxMonthlySyncStats:
    tenants: int = 0
    with_tin: int = 0
    rows_written: int = 0
    errors: int = 0


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(0)


def _month_paytax(tin, code, year, month, today, stats) -> Optional[Decimal]:
    """Bitta tin x kod x oy uchun payTax (period = oy boshidan oy oxirigacha)."""
    period_from = f"01.{month:02d}.{year}"
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    if year == today.year and month == today.month:
        end = today  # joriy oy — bugungacha
    period_to = end.strftime("%d.%m.%Y")
    try:
        data = soliq_service.get_company_account(tin, period_from, period_to, code) or {}
    except (soliq_service.SoliqError, requests.RequestException) as e:
        logger.warning("tax-monthly xato (tin=%s, kod=%s, %s-%s): %s", tin, code, year, month, e)
        stats.errors += 1
        return None
    return _to_decimal(data.get("payTax"))


def sync_tax_revenue_monthly(
    year: Optional[int] = None,
    only_current: bool = False,
    include_inactive: bool = False,
) -> TaxMonthlySyncStats:
    """
    year (default joriy) uchun oylik soliqni yig'adi. only_current=True bo'lsa —
    faqat joriy oy (kunlik celery uchun). Aks holda yil boshidan joriy oygacha
    barcha oylar (backfill). include_inactive=True bo'lsa nofaollar ham (tarix).
    """
    today = date.today()
    year = year or today.year
    last_month = today.month if year == today.year else 12
    months = [last_month] if only_current else list(range(1, last_month + 1))

    stats = TaxMonthlySyncStats()

    # Faol (yoki barcha) ijarachilarning takrorsiz tin lari.
    tins: set[str] = set()
    for tenant in ShopTenant.objects.all().iterator():
        stats.tenants += 1
        if not include_inactive and tenant.activity_status == ShopTenant.ActivityStatus.INACTIVE:
            continue
        tin = _resolve_tin(tenant)
        if tin:
            tins.add(tin)
    stats.with_tin = len(tins)

    for tin in tins:
        for code, _name in MONTHLY_TAX_CODES:
            for month in months:
                pay = _month_paytax(tin, code, year, month, today, stats)
                if pay is None:
                    continue
                with transaction.atomic():
                    TaxRevenueMonthly.objects.update_or_create(
                        tin=tin, tax_code=code, year=year, month=month,
                        defaults={"pay_tax": pay},
                    )
                stats.rows_written += 1

    return stats
