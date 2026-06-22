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
from django.db.models import Sum

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


def _ytd_paytax(tin, code, year, end_date, stats) -> Optional[Decimal]:
    """
    Yil boshidan `end_date` gacha KÜMÜLATİV payTax (YTD).

    company-account `periodFrom` ni e'tiborga olmaydi (doim yil boshidan), lekin
    `periodTo` ISHLAYDI — shuning uchun periodTo ni oy oxiriga qo'yib, shu oygacha
    yig'ilgan YTD payTax ni olamiz. Oylik qiymat YTD farqlaridan hisoblanadi.
    """
    period_to = end_date.strftime("%d.%m.%Y")
    try:
        data = soliq_service.get_company_account(tin, f"01.01.{year}", period_to, code) or {}
    except (soliq_service.SoliqError, requests.RequestException) as e:
        logger.warning("tax-monthly xato (tin=%s, kod=%s, ...%s): %s", tin, code, period_to, e)
        stats.errors += 1
        return None
    return _to_decimal(data.get("payTax"))


def _month_end(year, month, today):
    if year == today.year and month == today.month:
        return today  # joriy oy — bugungacha
    return date(year, month, calendar.monthrange(year, month)[1])


def sync_tax_revenue_monthly(
    year: Optional[int] = None,
    only_current: bool = False,
    include_inactive: bool = False,
) -> TaxMonthlySyncStats:
    """
    OYLIK soliq = YTD(oy oxiri) − YTD(oldingi oy oxiri) (company-account payTax,
    periodTo bo'yicha). year default joriy.

      - only_current=True: faqat JORIY oyni yangilaydi (kunlik celery) —
        joriy_oy = YTD(bugun) − (shu yil oldingi oylar yig'indisi). 1 so'rov/tin/kod.
      - aks holda: yil boshidan joriy oygacha BARCHA oylar (backfill) — har oy oxiri
        uchun YTD so'rab, ketma-ket delta. Backfill mumkin, chunki periodTo ishlaydi.
    """
    today = date.today()
    year = year or today.year
    last_month = today.month if year == today.year else 12

    stats = TaxMonthlySyncStats()

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
            if only_current:
                ytd = _ytd_paytax(tin, code, year, _month_end(year, last_month, today), stats)
                if ytd is None:
                    continue
                prior = TaxRevenueMonthly.objects.filter(
                    tin=tin, tax_code=code, year=year, month__lt=last_month
                ).aggregate(s=Sum("pay_tax"))["s"] or Decimal(0)
                _upsert_monthly(tin, code, year, last_month, ytd - prior)
                stats.rows_written += 1
                continue

            # To'liq backfill: har oy oxiri uchun YTD, ketma-ket delta.
            prev_ytd = Decimal(0)
            for month in range(1, last_month + 1):
                ytd = _ytd_paytax(tin, code, year, _month_end(year, month, today), stats)
                if ytd is None:
                    continue  # bu oy o'tkazildi; prev_ytd o'zgarmaydi
                _upsert_monthly(tin, code, year, month, ytd - prev_ytd)
                prev_ytd = ytd
                stats.rows_written += 1

    return stats


def _upsert_monthly(tin, code, year, month, value):
    with transaction.atomic():
        TaxRevenueMonthly.objects.update_or_create(
            tin=tin, tax_code=code, year=year, month=month,
            defaults={"pay_tax": value},
        )
