"""
Soliq (mspd-api.soliq.uz) integratsiyasi.

Uchta endpoint:
  1) self-employment                         — pinfl bo'yicha o'zini band qilgan shaxs ma'lumoti
  2) company-account                         — tin bo'yicha hisoblangan/to'langan soliqlar
  3) get-entrepreneur-activity-type-tax-rate — pinfl bo'yicha YaTT faoliyat turi va soliq stavkasi

DIQQAT: API faqat ruxsat etilgan server IP sidan ochiladi (localda DNS yo'q).
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# --- Config (shu faylning ichida) ------------------------------------------
BASE_URL    = "https://mspd-api.soliq.uz/akt/egovernment"
AUTH_HEADER = "Basic ZWdvdmVybm1lbnQ6RWdvdmVybm1lbnQtYS5wLmk="
# (connect, read) timeout — soliq sekin javob bersa ham ulanish tez tekshiriladi.
TIMEOUT     = (10, 30)
RETRIES     = 3
# ---------------------------------------------------------------------------


class SoliqError(Exception):
    """Soliq API muvaffaqiyatsiz javob qaytarganda (success=false yoki HTTP xato)."""


_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Vaqtincha timeout/5xx bo'lsa avtomatik qayta uradigan session."""
    global _session
    if _session is None:
        sess = requests.Session()
        retry = Retry(
            total=RETRIES,
            connect=RETRIES,
            read=RETRIES,
            backoff_factor=1,  # 0s, 1s, 2s, 4s ...
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        sess.mount("https://", adapter)
        sess.mount("http://", adapter)
        _session = sess
    return _session


def _headers() -> Dict[str, str]:
    return {"Authorization": AUTH_HEADER, "Accept": "application/json"}


def _request(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    method: str = "GET",
    json_body: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Soliqqa so'rov yuboradi, envelope ni tekshiradi va `data` ni qaytaradi.

    Endpointlar turli envelope ishlatadi, lekin hammada `success` bor:
      - self-employment:  success, reason,  status
      - company-account:  success, message, message_code
      - activity-rate:    success, errorCode, errorDescription
      - get-factura-data: success, message  (data — list)
    """
    url = f"{BASE_URL}/{path}"
    resp = _get_session().request(
        method, url, params=params, json=json_body, headers=_headers(), timeout=TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()

    if not body.get("success", False):
        reason = (
            body.get("reason")
            or body.get("message")
            or body.get("errorDescription")
            or "Noma'lum soliq API xatosi"
        )
        raise SoliqError(f"{path}: {reason}")

    return body.get("data")


def get_self_employment(pinfl: str) -> Optional[Dict[str, Any]]:
    """
    O'zini band qilgan shaxs ma'lumoti (pinfl bo'yicha).
    Qaytaradi: dict (pinfl, tin, first_name, last_name, middle_name,
               registration_number, registration_date, activities[...], ...) yoki None.
    """
    return _request("self-employment", {"pinfl": pinfl})


def get_company_account(
    tin: str,
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
    tax_code: int = 1,
) -> Optional[Dict[str, Any]]:
    """
    Hisoblangan va to'langan soliqlar (tin bo'yicha).
    Sana formati: dd.mm.yyyy. Berilmasa — joriy yil 1-yanvaridan bugungacha.
    """
    today = date.today()
    if not period_from:
        period_from = f"01.01.{today.year}"
    if not period_to:
        period_to = today.strftime("%d.%m.%Y")

    return _request(
        "company-account",
        {
            "periodFrom": period_from,
            "periodTo": period_to,
            "taxCode": tax_code,
            "tin": tin,
        },
    )


def get_entrepreneur_activity_tax_rate(pinfl: str) -> List[Dict[str, Any]]:
    """
    YaTT faoliyat turi va soliq stavkasi (pinfl bo'yicha).
    Qaytaradi: list (har biri: firm_name, activity_code, rate_summa,
               begin_date, end_date, iestatus1, iestatus2).
    """
    data = _request("get-entrepreneur-activity-type-tax-rate", {"isLogWrite": 0, "pinfl": pinfl})
    return data or []


def _full_name(data: Dict[str, Any]) -> Optional[str]:
    parts = [data.get("last_name"), data.get("first_name"), data.get("middle_name")]
    name = " ".join(p.strip() for p in parts if p and p.strip())
    return name or None


def soliq_fields_for(pinfl: Optional[str]) -> Dict[str, Any]:
    """
    pinfl bo'yicha soliqdan ShopTenant maydonlariga mos qiymatlarni oladi.
    Serializer ichida ishlatish uchun — hech qachon exception ko'tarmaydi,
    xato bo'lsa bo'sh dict qaytaradi (API hech qachon buzilmaydi).

    Qaytaradigan kalitlar (mavjud bo'lsa):
      stir, leader_fio, name, certificate_number, activity_status (1=active)
    """
    pinfl = (pinfl or "").strip()
    if not pinfl:
        return {}

    fields: Dict[str, Any] = {}

    try:
        se = get_self_employment(pinfl)
        if se:
            if se.get("tin"):
                fields["stir"] = str(se["tin"])
            fio = _full_name(se)
            if fio:
                fields["leader_fio"] = fio
            if se.get("registration_number"):
                fields["certificate_number"] = str(se["registration_number"])
    except (SoliqError, requests.RequestException) as e:
        logger.warning("soliq self-employment xato (pinfl=%s): %s", pinfl, e)

    try:
        rates = get_entrepreneur_activity_tax_rate(pinfl)
        if rates:
            first = rates[0]
            if first.get("firm_name"):
                fields["name"] = first["firm_name"]
            iestatus = first.get("iestatus1")
            if iestatus is not None:
                fields["activity_status"] = "active" if int(iestatus) == 1 else "inactive"
    except (SoliqError, requests.RequestException) as e:
        logger.warning("soliq activity-rate xato (pinfl=%s): %s", pinfl, e)

    return fields


# --- Faktura (elektron hisob-faktura) --------------------------------------

def get_factura_data(
    seller_tin: str,
    period_from: str,
    period_to: str,
    page: int = 0,
    size: int = 99,
    buyer_tin: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Bitta sahifa faktura ma'lumoti (sellerTin sotgan fakturalar).
    Sana formati: dd.mm.yyyy. Qaytaradi: list.
    """
    body: Dict[str, Any] = {
        "sellerTin": int(seller_tin),
        "page": page,
        "size": size,
        "periodFrom": period_from,
        "periodTo": period_to,
    }
    if buyer_tin:
        body["buyerTin"] = int(buyer_tin)

    data = _request("get-factura-data", method="POST", json_body=body)
    return data or []


def get_all_facturas(
    seller_tin: str,
    period_from: str,
    period_to: str,
    size: int = 99,
    max_pages: int = 200,
) -> List[Dict[str, Any]]:
    """Barcha sahifalarni yig'ib bitta ro'yxat qaytaradi."""
    out: List[Dict[str, Any]] = []
    page = 0
    while page < max_pages:
        batch = get_factura_data(seller_tin, period_from, period_to, page=page, size=size)
        if not batch:
            break
        out.extend(batch)
        if len(batch) < size:
            break
        page += 1
    return out


def _parse_factura_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except (ValueError, TypeError):
        return None


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal(0)


def factura_turnover_fields(tin: Optional[str], tax_type: Optional[str]) -> Dict[str, str]:
    """
    sellerTin (STIR) bo'yicha elektron faktura tushumini hisoblab,
    ShopTenant ning e_payment maydonlariga mos qiymat qaytaradi.

    Bir marta yil boshidan bugungacha oladi, ytd/mtd/dtd ni lokal hisoblaydi.
    tax_type='vat' -> *_vat, aks holda -> *_turnover.
    Xato bo'lsa bo'sh dict (API buzilmaydi).
    """
    tin = (tin or "").strip()
    if not tin:
        return {}

    today = date.today()
    period_from = f"01.01.{today.year}"
    period_to = today.strftime("%d.%m.%Y")

    try:
        facturas = get_all_facturas(tin, period_from, period_to)
    except (SoliqError, requests.RequestException) as e:
        logger.warning("soliq faktura xato (tin=%s): %s", tin, e)
        return {}

    ytd = mtd = dtd = Decimal(0)
    for f in facturas:
        amount = _to_decimal(f.get("deliverySumWithVat"))
        ytd += amount
        fd = _parse_factura_date(f.get("facturaDate"))
        if fd and fd.year == today.year and fd.month == today.month:
            mtd += amount
        if fd == today:
            dtd += amount

    suffix = "vat" if tax_type == "vat" else "turnover"
    return {
        f"ytd_e_payment_{suffix}": f"{ytd:.2f}",
        f"mtd_e_payment_{suffix}": f"{mtd:.2f}",
        f"dtd_e_payment_{suffix}": f"{dtd:.2f}",
    }


def aggregate_factura_by_day(
    seller_tin: str, period_from: str, period_to: str
) -> Dict[Any, Dict[str, Any]]:
    """
    sellerTin bo'yicha [period_from, period_to] oralig'idagi faktura'larni
    facturaDate (kun) bo'yicha yig'adi.

    Qaytaradi: { date(obyekt): {"sales": Decimal, "tax": Decimal, "count": int} }
    deliverySumWithVat -> sales, vatSum -> tax.
    """
    facturas = get_all_facturas(seller_tin, period_from, period_to)
    daily: Dict[Any, Dict[str, Any]] = {}
    for f in facturas:
        fd = _parse_factura_date(f.get("facturaDate"))
        if fd is None:
            continue
        bucket = daily.setdefault(fd, {"sales": Decimal(0), "tax": Decimal(0), "count": 0})
        bucket["sales"] += _to_decimal(f.get("deliverySumWithVat"))
        bucket["tax"] += _to_decimal(f.get("vatSum"))
        bucket["count"] += 1
    return daily
