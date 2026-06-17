"""
Kassa (onlayn-NKM / chek) faolligiga qarab rang.

Tenant (ijarachi) rangi:
  - green  : bugun chek urgan (cheques/summary, terminal bo'yicha) YOKI bugun faktura bor
  - yellow : kassa terminal (cash_register_number_vat/turnover) bor, lekin chek/faktura yo'q
  - red     : terminal ham, chek ham, faktura ham yo'q

Do'kon rangi (tenantlar bo'yicha):
  - hammasi green              -> green
  - hammasi red                -> red
  - aks holda (hammasi yellow,
    yoki aralash)              -> yellow
  - tenant yo'q                -> None
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from monitoring.services import soliq_service

# Kesh hali to'lmagan (warm task ishlamagan) — soliqqa bormay "noma'lum" rangi.
# Frontend buni kulrang/loading sifatida ko'rsatishi mumkin.
PENDING = "pending"


def _tenant_tin(tenant, cache_only: bool = False, force: bool = False) -> Optional[str]:
    """tin ni qaytaradi. cache_only va kesh bo'sh bo'lsa None (noma'lum)."""
    tin = (tenant.stir or "").strip()
    if tin:
        return tin
    fields = soliq_service.soliq_fields_for(
        tenant.leader_jshshir, cache_only=cache_only, force=force
    )
    if fields is None:  # cache_only: hali keshlanmagan
        return None
    return (fields.get("stir") or "").strip()


def _has_factura_today(tenant) -> bool:
    """Bugun faktura (e_payment) tushumi bormi — ShopTenant dtd (kun boshidan) maydonidan (tez)."""
    return ((tenant.dtd_e_payment_vat or 0) > 0) or ((tenant.dtd_e_payment_turnover or 0) > 0)


def tenant_cash_color(tenant, cache_only: bool = False, force: bool = False) -> str:
    """
    Tenant rangi:
      green  : BUGUN chek urgan (terminal bo'yicha) YOKI BUGUN faktura bor
      yellow : kassa terminal (cash_register_number_vat/turnover) bor, lekin chek/faktura yo'q
      red     : terminal ham, chek ham, faktura ham yo'q

    Chek — yangi cheques/summary API orqali (terminallar cash_register_number_vat
    va _turnover dan, ',' bilan ajratilgan). cache_only=True bo'lsa hech qachon
    soliqqa bormaydi (kesh bo'sh -> PENDING); force=True bo'lsa jonli o'qib qayta
    yozadi (warm task).
    """
    tin = _tenant_tin(tenant, cache_only=cache_only, force=force)
    if tin is None:  # soliq rekvizit hali keshlanmagan
        return PENDING

    terminals = soliq_service.parse_terminal_ids(
        tenant.cash_register_number_vat, tenant.cash_register_number_turnover
    )

    # 1) Chek (bugun, terminallar bo'yicha) — faqat terminal bor bo'lsa tekshiriladi.
    if tin and terminals:
        cheque = soliq_service.cheque_active(tin, terminals, cache_only=cache_only, force=force)
        if cheque is None:  # kesh hali to'lmagan
            return PENDING
        if cheque:
            return "green"

    # 2) Faktura (bugun) — tez, ShopTenant dtd maydonidan (soliqqa bormaydi).
    if _has_factura_today(tenant):
        return "green"

    # 3) Chek ham, faktura ham yo'q: terminal bo'lsa sariq, bo'lmasa qizil.
    return "yellow" if terminals else "red"


def shop_cash_status(shop, cache_only: bool = False, force: bool = False) -> Dict[str, Any]:
    """
    Do'kon kassa rangi. cache_only=True bo'lsa request thread ni bloklamaydi
    (soliqqa bormaydi); biror tenant ma'lumoti hali keshlanmagan bo'lsa
    do'kon rangi PENDING bo'ladi va warm task to'ldirgach yashil/qizil bo'ladi.
    force=True bo'lsa keshni e'tiborsiz qoldirib jonli soliqdan qayta yozadi (warm task).
    """
    tenants = list(shop.tenants.all())
    total = len(tenants)
    if total == 0:
        return {"color": None, "green": 0, "total": 0}

    colors = [tenant_cash_color(t, cache_only=cache_only, force=force) for t in tenants]

    if PENDING in colors:
        return {"color": PENDING, "green": 0, "total": total}

    green = sum(1 for c in colors if c == "green")
    red = sum(1 for c in colors if c == "red")
    if green == total:
        color = "green"
    elif red == total:  # faqat hamma tenant red bo'lsagina do'kon red
        color = "red"
    else:               # hammasi yellow, yoki aralash -> yellow
        color = "yellow"

    return {"color": color, "green": green, "total": total}
