"""
Ijara (rent) integratsiyasi: do'kon egasidan ijarachilarni olib ShopTenant ga yozadi.

Har do'kon (Shop) uchun:
  egasi (owner_jshshir=pinfl) + cadastr_number
    -> rent API (justice)
    -> ijara shartnomalari (to* = ijarachi)
    -> ShopTenant create/update

Qoida: ijaraga beruvchi jismoniy -> pinfl, yuridik -> tin. Bizning Shop'da
owner_jshshir (pinfl) bor, shuning uchun pinfl bilan so'raladi.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from django.utils import timezone

from monitoring.models import Shop, ShopTenant
from monitoring.services import soliq_service

logger = logging.getLogger(__name__)

STATE_ACTIVE = 20  # "Tasdiqlangan"


@dataclass
class RentSyncStats:
    shops: int = 0
    with_owner_cadastr: int = 0
    tenants_created: int = 0
    tenants_updated: int = 0
    tenants_deactivated: int = 0
    errors: int = 0


def _to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _business_type(to_user_type):
    s = str(to_user_type or "").strip()
    if s == "2":
        return ShopTenant.BusinessType.LEGAL
    if s == "1":
        return ShopTenant.BusinessType.YTT
    return ShopTenant.BusinessType.OTHER


def _pick_best_per_tenant(agreements):
    """Bir ijarachi uchun bir nechta shartnoma bo'lsa — faolini (state=20) afzal ko'radi."""
    best = {}
    for a in agreements:
        key = str(a.get("toTin") or "") + "|" + str(a.get("toPinfl") or "")
        if key == "|":
            continue
        cur = best.get(key)
        if cur is None or (a.get("state") == STATE_ACTIVE and cur.get("state") != STATE_ACTIVE):
            best[key] = a
    return best


def _upsert_tenant(shop, a, stats):
    """Ijarachini yaratadi/yangilaydi. Tegilgan ShopTenant pk sini qaytaradi
    (identifikatori yo'q bo'lsa None) — chaqiruvchi 'ko'rilgan'larni belgilashi uchun."""
    to_tin = (str(a.get("toTin")).strip() if a.get("toTin") else None)
    to_pinfl = (str(a.get("toPinfl")).strip() if a.get("toPinfl") else None)

    defaults = {
        "shop": shop,
        "name": a.get("toYurName") or a.get("toFio"),
        "leader_fio": a.get("toFio"),
        "leader_phone": str(a.get("toPhone")) if a.get("toPhone") else None,
        "stir": to_tin,
        "leader_jshshir": to_pinfl,
        "business_type": _business_type(a.get("toUserType")),
        "rented_area": _to_decimal(a.get("rentField")),
        "activity_status": (
            ShopTenant.ActivityStatus.ACTIVE if a.get("state") == STATE_ACTIVE
            else ShopTenant.ActivityStatus.INACTIVE
        ),
    }

    # Lookup: stir bo'lsa shu bo'yicha, aks holda pinfl bo'yicha (do'kon ichida)
    if to_tin:
        lookup = {"shop": shop, "stir": to_tin}
    elif to_pinfl:
        lookup = {"shop": shop, "leader_jshshir": to_pinfl}
    else:
        return None

    obj = ShopTenant.objects.filter(**lookup).first()
    if obj:
        # Mavjud yozuvni yangilaymiz, lekin BO'SH (None/"") qiymat bilan ustiga
        # yozmaymiz — eski ma'lumot (telefon, avatar va h.k.) o'chib ketmasin.
        for k, v in defaults.items():
            if v is None or v == "":
                continue
            setattr(obj, k, v)
        obj.save()
        stats.tenants_updated += 1
        return obj.pk

    obj = ShopTenant.objects.create(**defaults)
    stats.tenants_created += 1
    return obj.pk


def sync_tenants_from_rent(only_shop_id: Optional[int] = None) -> RentSyncStats:
    stats = RentSyncStats()

    qs = Shop.objects.exclude(cadastr_number__isnull=True).exclude(cadastr_number__exact="")
    if only_shop_id:
        qs = qs.filter(pk=only_shop_id)

    for shop in qs.iterator():
        stats.shops += 1
        pinfl = (shop.owner_jshshir or "").strip()
        cadastr = (shop.cadastr_number or "").strip()
        if not pinfl or not cadastr:
            continue
        stats.with_owner_cadastr += 1

        try:
            agreements = soliq_service.get_rent_information(pinfl=pinfl, cadastr=cadastr)
        except (soliq_service.SoliqError, requests.RequestException) as e:
            logger.warning("rent sync xato (shop=%s): %s", shop.pk, e)
            stats.errors += 1
            continue

        seen_pks: set[int] = set()
        for a in _pick_best_per_tenant(agreements).values():
            try:
                pk = _upsert_tenant(shop, a, stats)
                if pk is not None:
                    seen_pks.add(pk)
            except Exception as e:
                logger.warning("rent tenant upsert xato (shop=%s): %s", shop.pk, e)
                stats.errors += 1

        # Rent API muvaffaqiyatli javob berdi (xato bo'lsa yuqorida `continue`).
        # Shu do'konda javobda kelmagan, hali NOFAOL bo'lmagan ijarachilarni
        # NOFAOL belgilaymiz — o'chirmaymiz (keyingi sync ularni qaytarsa yana
        # ACTIVE bo'ladi).
        deactivated = (
            ShopTenant.objects
            .filter(shop=shop)
            .exclude(pk__in=seen_pks)
            .exclude(activity_status=ShopTenant.ActivityStatus.INACTIVE)
            .update(
                activity_status=ShopTenant.ActivityStatus.INACTIVE,
                updated_time=timezone.now(),
            )
        )
        stats.tenants_deactivated += deactivated

    return stats
