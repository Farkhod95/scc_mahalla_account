"""
Kassa (onlayn-NKM / chek) faolligiga qarab rang.

Tenant (ijarachi) rangi:
  - green  : joriy oyda chek urgan (nkm_active)
  - yellow : kassa apparati ro'yxatda bor, lekin chek yo'q
  - red     : kassa ham yo'q, chek ham yo'q

Do'kon rangi (tenantlar bo'yicha):
  - hammasi green        -> green
  - hech biri green emas -> red
  - qisman               -> yellow
  - tenant yo'q          -> None
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from monitoring.services import soliq_service

# Kesh hali to'lmagan (warm task ishlamagan) — soliqqa bormay "noma'lum" rangi.
# Frontend buni kulrang/loading sifatida ko'rsatishi mumkin.
PENDING = "pending"


def _tenant_tin(tenant, cache_only: bool = False) -> Optional[str]:
    """tin ni qaytaradi. cache_only va kesh bo'sh bo'lsa None (noma'lum)."""
    tin = (tenant.stir or "").strip()
    if tin:
        return tin
    fields = soliq_service.soliq_fields_for(tenant.leader_jshshir, cache_only=cache_only)
    if fields is None:  # cache_only: hali keshlanmagan
        return None
    return (fields.get("stir") or "").strip()


def _has_registered_kassa(tenant) -> bool:
    return bool(
        (tenant.cash_register_number_vat or "").strip()
        or (tenant.cash_register_number_turnover or "").strip()
    )


def tenant_cash_color(tenant, cache_only: bool = False) -> str:
    """
    Tenant rangi. cache_only=True bo'lsa hech qachon soliqqa bormaydi —
    kerakli ma'lumot hali keshlanmagan bo'lsa PENDING qaytaradi.
    """
    tin = _tenant_tin(tenant, cache_only=cache_only)
    if tin is None:  # soliq fields hali keshlanmagan
        return PENDING
    if tin:
        active = soliq_service.nkm_active(tin, cache_only=cache_only)
        if active is None:  # nkm hali keshlanmagan
            return PENDING
        if active:
            return "green"
    return "yellow" if _has_registered_kassa(tenant) else "red"


def shop_cash_status(shop, cache_only: bool = False) -> Dict[str, Any]:
    """
    Do'kon kassa rangi. cache_only=True bo'lsa request thread ni bloklamaydi
    (soliqqa bormaydi); biror tenant ma'lumoti hali keshlanmagan bo'lsa
    do'kon rangi PENDING bo'ladi va warm task to'ldirgach yashil/qizil bo'ladi.
    """
    tenants = list(shop.tenants.all())
    total = len(tenants)
    if total == 0:
        return {"color": None, "green": 0, "total": 0}

    colors = [tenant_cash_color(t, cache_only=cache_only) for t in tenants]

    if PENDING in colors:
        return {"color": PENDING, "green": 0, "total": total}

    green = sum(1 for c in colors if c == "green")
    if green == total:
        color = "green"
    elif green == 0:
        color = "red"
    else:
        color = "yellow"

    return {"color": color, "green": green, "total": total}
