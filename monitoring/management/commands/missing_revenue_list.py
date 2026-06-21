"""
"Savdo tushumlari kam" diagnostikasi: integratsiyadan (soliq) tushum ma'lumoti
KELMAGAN tenantlar ro'yxati — PINFL/STIR bilan.

Har faol ShopTenant uchun tin aniqlanadi (MCHJ -> STIR, YTT -> PINFL->soliq) va
tin bo'yicha FacturaRevenueDaily / OkkmRevenueDaily da yozuv bor-yo'qligi
tekshiriladi. Yozuv bo'lmasa tenant ro'yxatga tushadi:
  - tin_aniqlanmadi          : STIR yo'q va PINFL->soliq tin bermadi (JShShIR topilmadi)
  - integratsiya_malumoti_yoq: tin bor, lekin Factura ham OKKM ham bo'sh

DIQQAT: soliqqa boradi (YTT tin resolve) — soliq ochiladigan SERVERDA ishlating.
Natija stdout + CSV faylga yoziladi.

    python manage.py missing_revenue_list
    python manage.py missing_revenue_list --year 2026 --out docs/missing_2026.csv
    python manage.py missing_revenue_list --include-inactive
"""
import csv
import logging
import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from monitoring.models import FacturaRevenueDaily, OkkmRevenueDaily, ShopTenant
from monitoring.services.revenue_sync import _resolve_tin

TYPE_LABEL = {
    ShopTenant.BusinessType.YTT: "YTT",
    ShopTenant.BusinessType.LEGAL: "MCHJ",
    ShopTenant.BusinessType.OTHER: "Boshqa",
}


class Command(BaseCommand):
    help = "Integratsiyadan tushum ma'lumoti kelmagan tenantlar (PINFL/STIR) ro'yxati."

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, default=None, help="Yil (default: joriy)")
        parser.add_argument("--out", default=None, help="CSV yo'li (default: docs/missing_revenue_<yil>.csv)")
        parser.add_argument("--include-inactive", action="store_true", help="NOFAOL tenantlarni ham tekshiradi")

    def handle(self, *args, **opts):
        # soliq resolve xatolari (JShShIR topilmadi) log spam qilmasin.
        logging.getLogger("monitoring.services.revenue_sync").setLevel(logging.ERROR)

        year = opts["year"] or date.today().year
        out_path = opts["out"] or os.path.join(settings.BASE_DIR, "docs", f"missing_revenue_{year}.csv")

        qs = ShopTenant.objects.select_related("shop").all()
        if not opts["include_inactive"]:
            qs = qs.exclude(activity_status=ShopTenant.ActivityStatus.INACTIVE)

        # tin keshi (pinfl -> tin) — bir pinfl uchun soliqqa bir marta.
        tin_cache: dict = {}
        # tin -> (has_factura, has_okkm) keshi
        data_cache: dict = {}

        def has_data(tin):
            if tin not in data_cache:
                f = FacturaRevenueDaily.objects.filter(seller_tin=tin, date__year=year).exists()
                o = OkkmRevenueDaily.objects.filter(tin=tin, date__year=year).exists()
                data_cache[tin] = (f, o)
            return data_cache[tin]

        rows = []
        total = checked = 0
        for t in qs.iterator():
            total += 1
            stir = (t.stir or "").strip()
            pinfl = (t.leader_jshshir or "").strip()

            if stir:
                tin = stir
            else:
                if pinfl in tin_cache:
                    tin = tin_cache[pinfl]
                else:
                    tin = _resolve_tin(t)
                    tin_cache[pinfl] = tin
            checked += 1

            if not tin:
                reason = "tin_aniqlanmadi"
                has_f = has_o = False
            else:
                has_f, has_o = has_data(tin)
                if has_f or has_o:
                    continue  # tushum bor — ro'yxatga tushmaydi
                reason = "integratsiya_malumoti_yoq"

            rows.append({
                "tenant_id": t.pk,
                "name": t.name or t.leader_fio or "",
                "type": TYPE_LABEL.get(t.business_type, ""),
                "stir": stir,
                "pinfl": pinfl,
                "tin": tin or "",
                "shop": str(t.shop) if t.shop_id else "",
                "reason": reason,
            })

        # CSV
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fields = ["tenant_id", "name", "type", "stir", "pinfl", "tin", "shop", "reason"]
        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

        no_tin = sum(1 for r in rows if r["reason"] == "tin_aniqlanmadi")
        no_data = sum(1 for r in rows if r["reason"] == "integratsiya_malumoti_yoq")
        uniq_ids = sorted({(r["stir"] or r["pinfl"]) for r in rows if (r["stir"] or r["pinfl"])})

        self.stdout.write(self.style.SUCCESS(
            f"Tekshirildi: {checked}/{total} tenant ({year}). "
            f"Tushumsiz: {len(rows)} (tin_aniqlanmadi={no_tin}, integratsiya_malumoti_yoq={no_data})"
        ))
        self.stdout.write(f"Noyob STIR/PINFL: {len(uniq_ids)} ta")
        self.stdout.write(f"CSV: {out_path}\n")

        for r in rows:
            self.stdout.write(
                f"  {r['type']:6} STIR={r['stir'] or '-':12} PINFL={r['pinfl'] or '-':16} "
                f"{r['reason']:24} | {r['name']} | {r['shop']}"
            )
