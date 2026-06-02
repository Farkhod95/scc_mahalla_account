"""
Faktura tushumini kunlik tarix jadvaliga (FacturaRevenueDaily) yig'ish.

Davriy (cron/celery) ishlaydi: har bir tenant ning STIR (sellerTin) bo'yicha
faktura'larni olib, kun bo'yicha yig'adi va upsert qiladi. Dashboard grafigi
shu jadvaldan o'qiydi (jonli soliq so'rovi yo'q).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

import requests
from django.db import transaction

from monitoring.models import ShopTenant, FacturaRevenueDaily
from monitoring.services import soliq_service

logger = logging.getLogger(__name__)


@dataclass
class RevenueSyncStats:
    tenants: int = 0
    with_tin: int = 0
    days_written: int = 0
    errors: int = 0


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
        logger.warning("tin resolve xato (tenant=%s): %s", tenant.pk, e)
        return None
    if se and se.get("tin"):
        return str(se["tin"]).strip()
    return None


def sync_factura_revenue(period_from: Optional[str] = None, period_to: Optional[str] = None) -> RevenueSyncStats:
    """
    Berilgan davr uchun barcha tenantlarning faktura tushumini yig'adi.
    Davr berilmasa — joriy yil 1-yanvaridan bugungacha.
    """
    today = date.today()
    if not period_from:
        period_from = f"01.01.{today.year}"
    if not period_to:
        period_to = today.strftime("%d.%m.%Y")

    stats = RevenueSyncStats()
    seen_tins: set[str] = set()

    for tenant in ShopTenant.objects.all().iterator():
        stats.tenants += 1
        tin = _resolve_tin(tenant)
        if not tin or tin in seen_tins:
            continue
        seen_tins.add(tin)
        stats.with_tin += 1

        try:
            daily = soliq_service.aggregate_factura_by_day(tin, period_from, period_to)
        except (soliq_service.SoliqError, requests.RequestException) as e:
            logger.warning("faktura sync xato (tin=%s): %s", tin, e)
            stats.errors += 1
            continue

        with transaction.atomic():
            for day, agg in daily.items():
                FacturaRevenueDaily.objects.update_or_create(
                    date=day,
                    seller_tin=tin,
                    defaults={
                        "sales": agg["sales"],
                        "tax": agg["tax"],
                        "factura_count": agg["count"],
                    },
                )
                stats.days_written += 1

    return stats
