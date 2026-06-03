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

from typing import Any, Dict

from monitoring.services import soliq_service


def _tenant_tin(tenant) -> str:
    tin = (tenant.stir or "").strip()
    if tin:
        return tin
    fields = soliq_service.soliq_fields_for(tenant.leader_jshshir)  # keshlangan
    return (fields.get("stir") or "").strip()


def _has_registered_kassa(tenant) -> bool:
    return bool(
        (tenant.cash_register_number_vat or "").strip()
        or (tenant.cash_register_number_turnover or "").strip()
    )


def tenant_cash_color(tenant) -> str:
    tin = _tenant_tin(tenant)
    if tin and soliq_service.nkm_active(tin):
        return "green"
    return "yellow" if _has_registered_kassa(tenant) else "red"


def shop_cash_status(shop) -> Dict[str, Any]:
    tenants = list(shop.tenants.all())
    total = len(tenants)
    if total == 0:
        return {"color": None, "green": 0, "total": 0}

    green = sum(1 for t in tenants if tenant_cash_color(t) == "green")
    if green == total:
        color = "green"
    elif green == 0:
        color = "red"
    else:
        color = "yellow"

    return {"color": color, "green": green, "total": total}
