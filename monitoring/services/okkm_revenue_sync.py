"""
OKKM (NKM cheklar) kunlik tushumini OkkmRevenueDaily ga yig'ish.

Factura'dan farqi: soliqda OKKM ni kunlarga bo'lib beradigan arzon endpoint yo'q,
shuning uchun [period_from, period_to] oralig'idagi HAR KUN uchun alohida
get_cheque_statistics(tin, kun, kun) chaqiriladi va upsert qilinadi.

  - kunlik sync (celery beat): davr berilmaydi -> faqat BUGUN (1 kun, arzon).
  - backfill (management command): --from/--to bilan o'tgan kunlar (ko'p kun, sekin) — BIR MARTA.

Nofaol ijarachi skip qilinadi (faktura sync bilan bir xil qoida). Bo'sh kun (0)
yozilmaydi — jadval shishmaydi.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from django.db import transaction

from monitoring.models import ShopTenant, OkkmRevenueDaily
from monitoring.services import soliq_service

logger = logging.getLogger(__name__)


@dataclass
class OkkmRevenueSyncStats:
    tenants: int = 0
    skipped_inactive: int = 0
    with_tin: int = 0
    days_written: int = 0
    errors: int = 0


def _to_decimal(value) -> Optional[Decimal]:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except (ValueError, TypeError):
        return None


def _daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _resolve_tin(tenant: ShopTenant) -> Optional[str]:
    """tenant.stir bo'lsa o'sha, aks holda pinfl orqali self-employment'dan tin."""
    tin = (tenant.stir or "").strip()
    if tin:
        return tin
    pinfl = (tenant.leader_jshshir or "").strip()
    if not pinfl:
        return None
    try:
        se = soliq_service.get_self_employment(pinfl)
    except (soliq_service.SoliqError, requests.RequestException) as e:
        logger.warning("okkm tin resolve xato (tenant=%s): %s", tenant.pk, e)
        return None
    if se and se.get("tin"):
        return str(se["tin"]).strip()
    return None


def sync_okkm_revenue(
    period_from: Optional[str] = None, period_to: Optional[str] = None
) -> OkkmRevenueSyncStats:
    """
    [period_from, period_to] oralig'idagi har kun uchun har faol tenant ning OKKM
    tushumini OkkmRevenueDaily ga upsert qiladi. Davr berilmasa — faqat bugun.
    Sana formati: dd.mm.yyyy.
    """
    today = date.today()
    start = _parse(period_from) or today
    end = _parse(period_to) or today

    stats = OkkmRevenueSyncStats()
    seen_tins: set[str] = set()

    for tenant in ShopTenant.objects.all().iterator():
        stats.tenants += 1

        # Nofaol ijarachi: OKKM tushumi yig'ilmaydi (faktura sync bilan bir xil).
        if tenant.activity_status == ShopTenant.ActivityStatus.INACTIVE:
            stats.skipped_inactive += 1
            continue

        tin = _resolve_tin(tenant)
        if not tin or tin in seen_tins:
            continue
        seen_tins.add(tin)
        stats.with_tin += 1

        for day in _daterange(start, end):
            day_str = day.strftime("%d.%m.%Y")
            try:
                st = soliq_service.get_cheque_statistics(tin, day_str, day_str) or {}
            except (requests.RequestException, ValueError) as e:
                logger.warning("okkm cheque-stats xato (tin=%s, %s): %s", tin, day_str, e)
                stats.errors += 1
                continue

            turnover = _to_decimal(st.get("turnover")) or Decimal(0)
            vat = _to_decimal(st.get("vat")) or Decimal(0)
            count = int(st.get("chequeCount") or 0)

            # Bo'sh kun (savdosiz) yozilmaydi — jadval shishmaydi.
            if turnover == 0 and vat == 0 and count == 0:
                continue

            with transaction.atomic():
                OkkmRevenueDaily.objects.update_or_create(
                    date=day,
                    tin=tin,
                    defaults={"turnover": turnover, "vat": vat, "cheque_count": count},
                )
            stats.days_written += 1

    return stats
