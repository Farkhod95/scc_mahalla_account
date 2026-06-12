"""
OKKM (NKM cheklar) kunlik tushumini OkkmRevenueDaily ga yig'ish.

Yangi egovernment `cheques/summary` endpointidan o'qiydi: u tin + terminalId
talab qiladi, shuning uchun har faol ijarachining cash_register_number_vat va
_turnover ('A,B' — ',' bilan ajratilgan) terminallari bo'yicha so'raladi va tin
bo'yicha yig'iladi. Soliqda OKKM ni kunlarga bo'lib beradigan endpoint yo'q, shuning uchun
[period_from, period_to] oralig'idagi HAR KUN alohida (dateFrom=dateTo=kun)
chaqirilib upsert qilinadi.

  - kunlik sync (celery beat): davr berilmaydi -> faqat BUGUN.
  - backfill (management command): --from/--to bilan o'tgan kunlar (sekin) — BIR MARTA.

Nofaol ijarachi va terminal(vat)siz tin skip qilinadi. Bo'sh kun (0) yozilmaydi —
jadval shishmaydi.
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
    cleared: int = 0


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
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
    clear: bool = False,
) -> OkkmRevenueSyncStats:
    """
    [period_from, period_to] oralig'idagi har kun uchun har faol tenant ning OKKM
    tushumini OkkmRevenueDaily ga upsert qiladi. Davr berilmasa — faqat bugun.
    Sana formati: dd.mm.yyyy.

    clear=True bo'lsa: sync'dan oldin [start, end] oralig'idagi BARCHA OkkmRevenueDaily
    yozuvlari o'chiriladi (endi yig'ilmaydigan/stale tin'lar ham tozalanadi), so'ng
    qaytadan to'liq yoziladi. Faqat qo'lda backfill uchun (beat hech qachon clear qilmaydi).
    """
    today = date.today()
    start = _parse(period_from) or today
    end = _parse(period_to) or today

    stats = OkkmRevenueSyncStats()

    if clear:
        deleted, _ = OkkmRevenueDaily.objects.filter(
            date__gte=start, date__lte=end
        ).delete()
        stats.cleared = deleted

    # 1) tin -> terminallar (faol ijarachilarning cash_register_number_vat/turnover dan).
    #    Bir tin bir nechta tenant qatorida bo'lsa, terminallari birlashtiriladi.
    tin_terminals: dict[str, set] = {}
    for tenant in ShopTenant.objects.all().iterator():
        stats.tenants += 1

        # Nofaol ijarachi: OKKM tushumi yig'ilmaydi (faktura sync bilan bir xil).
        if tenant.activity_status == ShopTenant.ActivityStatus.INACTIVE:
            stats.skipped_inactive += 1
            continue

        tin = _resolve_tin(tenant)
        if not tin:
            continue
        terminals = soliq_service.parse_terminal_ids(
            tenant.cash_register_number_vat, tenant.cash_register_number_turnover
        )
        if not terminals:  # terminalsiz tin -> yangi API ni so'rab bo'lmaydi
            continue
        tin_terminals.setdefault(tin, set()).update(terminals)

    stats.with_tin = len(tin_terminals)

    # 2) Har tin x har kun: terminallar bo'yicha yig'ib upsert.
    for tin, terminals in tin_terminals.items():
        for day in _daterange(start, end):
            day_str = day.strftime("%Y-%m-%d")  # yangi API: ISO sana
            count = 0
            turnover = Decimal(0)
            vat = Decimal(0)
            for terminal in terminals:
                try:
                    s = soliq_service.get_cheque_summary(tin, terminal, day_str, day_str)
                except (requests.RequestException, ValueError) as e:
                    logger.warning(
                        "okkm cheque-summary xato (tin=%s, term=%s, %s): %s",
                        tin, terminal, day_str, e,
                    )
                    stats.errors += 1
                    continue
                if not s:
                    continue
                count += int(s.get("chequeCount") or 0)
                turnover += _to_decimal(s.get("turnover")) or Decimal(0)
                vat += _to_decimal(s.get("vat")) or Decimal(0)

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
