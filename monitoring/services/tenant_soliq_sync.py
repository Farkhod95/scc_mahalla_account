"""
Soliq ma'lumotini (rekvizit + faktura tushumi) ShopTenant maydonlariga yozish.

Davriy (celery beat) ishlaydi va bu yerda jonli soliqqa boriladi (FON da).
Maqsad: shop-tenant API lari (ro'yxat/detal) request thread da soliqqa
bormasin — to'g'ridan-to'g'ri bazadan o'qisin va hech narsa bloklanmasin.
(ASGI/daphne ostida sinxron view lar bitta umumiy thread da ishlaydi.)

Source of truth = SOLIQ: soliqdan qiymat kelsa, DB dagi (Excel/qo'l) qiymat
ustiga yoziladi. Soliq xato/bo'sh bo'lsa — DB dagi qiymat o'zgarmaydi.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from django.db import transaction

from monitoring.models import ShopTenant
from monitoring.services import soliq_service

logger = logging.getLogger(__name__)

# soliq_fields_for kalitlari -> ShopTenant maydonlari (nomi bir xil).
_REQUISITE_KEYS = ("stir", "leader_fio", "certificate_number", "name", "activity_status")


@dataclass
class TenantSoliqSyncStats:
    tenants: int = 0
    updated: int = 0
    errors: int = 0


def _to_decimal(value) -> Optional[Decimal]:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _cheque_fields(tin: str, tax_type) -> dict:
    """
    NKM cheklar statistikasidan ShopTenant OKKM/cheklar maydonlariga qiymat.

    tax_type ga qarab _vat yoki _turnover ustuniga yoziladi:
      ytd/mtd/dtd_okkm_{suffix}            <- turnover (OKKM savdo tushumi)
      monthly/daily_checks_count_{suffix}  <- chequeCount (cheklar soni)

    YTD cheklar soni uchun modelda maydon yo'q — faqat tushum yoziladi.
    """
    suffix = "vat" if tax_type == ShopTenant.TaxType.VAT else "turnover"
    today = date.today()
    today_str = today.strftime("%d.%m.%Y")
    periods = {
        "ytd": (f"01.01.{today.year}", today_str),
        "mtd": (today.strftime("01.%m.%Y"), today_str),
        "dtd": (today_str, today_str),
    }

    out: dict = {}
    for label, (pf, pt) in periods.items():
        try:
            stats = soliq_service.get_cheque_statistics(tin, pf, pt) or {}
        except (requests.RequestException, ValueError) as e:
            logger.warning("cheque-stats xato (tin=%s, %s): %s", tin, label, e)
            continue

        turnover = _to_decimal(stats.get("turnover"))
        if turnover is not None:
            out[f"{label}_okkm_{suffix}"] = turnover

        count = stats.get("chequeCount")
        if count is not None:
            if label == "mtd":
                out[f"monthly_checks_count_{suffix}"] = int(count)
            elif label == "dtd":
                out[f"daily_checks_count_{suffix}"] = int(count)

    return out


def _sync_one(tenant: ShopTenant) -> bool:
    """Bitta tenant ni soliqdan yangilaydi. O'zgargan bo'lsa True qaytaradi."""
    changed = {}

    # 1) Rekvizit (pinfl/leader_jshshir bo'yicha).
    fields = soliq_service.soliq_fields_for(tenant.leader_jshshir) or {}
    for key in _REQUISITE_KEYS:
        val = fields.get(key)
        if val:
            changed[key] = val

    # 2) Faktura tushumi (tin bo'yicha): ytd/mtd/dtd_e_payment_{vat|turnover}.
    tin = (changed.get("stir") or tenant.stir or "").strip()
    if tin:
        factura = soliq_service.factura_turnover_fields(tin, tenant.tax_type)
        for key, val in factura.items():
            dec = _to_decimal(val)
            if dec is not None:
                changed[key] = dec

        # 3) NKM cheklar (OKKM tushum + cheklar soni) — tin bo'yicha ytd/mtd/dtd.
        changed.update(_cheque_fields(tin, tenant.tax_type))

    if not changed:
        return False

    for field, val in changed.items():
        setattr(tenant, field, val)
    # updated_time (auto_now) ham yangilanishi uchun update_fields ga qo'shamiz.
    with transaction.atomic():
        tenant.save(update_fields=list(changed.keys()) + ["updated_time"])
    return True


def sync_tenant_soliq() -> TenantSoliqSyncStats:
    """Barcha tenantlarning soliq maydonlarini bazaga yozadi."""
    stats = TenantSoliqSyncStats()

    for tenant in ShopTenant.objects.all().iterator():
        stats.tenants += 1
        try:
            if _sync_one(tenant):
                stats.updated += 1
        except Exception as e:  # bitta tenant xatosi butun sync ni to'xtatmasin
            logger.warning("tenant soliq sync xato (tenant=%s): %s", tenant.pk, e)
            stats.errors += 1

    return stats
