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
from decimal import Decimal, InvalidOperation
from typing import Optional

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
