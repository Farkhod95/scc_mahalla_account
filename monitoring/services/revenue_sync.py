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
    skipped_inactive: int = 0
    with_tin: int = 0
    days_written: int = 0
    errors: int = 0


def _tin_from_pinfl(tenant: ShopTenant) -> Optional[str]:
    """pinfl (leader_jshshir) orqali self-employment'dan tin. Xato/yo'q bo'lsa None."""
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


def _resolve_tin(tenant: ShopTenant) -> Optional[str]:
    """
    Revenue (faktura/OKKM) qaysi tin bo'yicha olinishi — tashkilot turidan qat'i nazar:
      - STIR bo'lsa -> STIR (MCHJ, yoki STIR'i bor YTT);
      - STIR bo'lmasa -> PINFL (leader_jshshir) orqali self-employment tin.

    sync_factura_revenue (sync-factura-revenue-daily) va sync_okkm_revenue
    (sync-okkm-revenue-daily) ikkalasi ham shu funksiyani ishlatadi.
    """
    stir = (tenant.stir or "").strip()
    if stir:
        return stir
    return _tin_from_pinfl(tenant)


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

        # Nofaol ijarachi: eski FacturaRevenueDaily yozuvlari o'chmaydi (qoladi),
        # lekin bugundan keyin yangi kun ma'lumoti yig'ilmaydi — skip qilamiz.
        if tenant.activity_status == ShopTenant.ActivityStatus.INACTIVE:
            stats.skipped_inactive += 1
            continue

        # Faktura: STIR bo'lsa STIR bo'yicha, bo'lmasa to'g'ridan-to'g'ri PINFL
        # (leader_jshshir) bo'yicha olamiz. Ikkalasi ham soliq faktura `pin`
        # maydoniga yuboriladi (pin STIR ham, PINFL ham qabul qiladi). Soliqdan
        # TIN resolve qilinmaydi — STIR'siz YTT data'si PINFL kaliti bilan saqlanadi.
        tin = (tenant.stir or "").strip() or (tenant.leader_jshshir or "").strip()
        if not tin or tin in seen_tins:
            continue
        seen_tins.add(tin)
        stats.with_tin += 1

        try:
            daily = soliq_service.aggregate_factura_by_day(tin, period_from, period_to)
        except (soliq_service.SoliqError, requests.RequestException) as e:
            logger.warning("faktura sync xato (pin=%s): %s", tin, e)
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
