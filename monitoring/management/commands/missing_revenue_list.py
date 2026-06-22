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

    python manage.py missing_revenue_list                      # both: factura ham, okkm ham yo'q
    python manage.py missing_revenue_list --channel factura    # fakturasi yo'qlar ro'yxati
    python manage.py missing_revenue_list --channel okkm       # OKKM'i yo'qlar
    python manage.py missing_revenue_list --year 2026 --include-inactive
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
        parser.add_argument("--out", default=None, help="CSV yo'li (default: docs/missing_<channel>_<yil>.csv)")
        parser.add_argument("--include-inactive", action="store_true", help="NOFAOL tenantlarni ham tekshiradi")
        parser.add_argument(
            "--channel", choices=["both", "factura", "okkm"], default="both",
            help="factura=fakturasi yo'qlar, okkm=OKKM'i yo'qlar, both=ikkalasi ham yo'q (default: both)",
        )

    def handle(self, *args, **opts):
        # soliq resolve xatolari (JShShIR topilmadi) log spam qilmasin.
        logging.getLogger("monitoring.services.revenue_sync").setLevel(logging.ERROR)

        year = opts["year"] or date.today().year
        channel = opts["channel"]
        out_path = opts["out"] or os.path.join(settings.BASE_DIR, "docs", f"missing_{channel}_{year}.csv")

        qs = ShopTenant.objects.select_related("shop").all()
        if not opts["include_inactive"]:
            qs = qs.exclude(activity_status=ShopTenant.ActivityStatus.INACTIVE)

        # tin keshi (pinfl -> tin) — bir pinfl uchun soliqqa bir marta.
        tin_cache: dict = {}
        # tin -> (has_factura, has_okkm) keshi
        data_cache: dict = {}

        def has_factura(key):
            if key not in data_cache:
                data_cache[key] = FacturaRevenueDaily.objects.filter(
                    seller_tin=key, date__year=year).exists()
            return data_cache[key]

        def has_okkm(tin):
            ckey = f"okkm:{tin}"
            if ckey not in data_cache:
                data_cache[ckey] = OkkmRevenueDaily.objects.filter(
                    tin=tin, date__year=year).exists()
            return data_cache[ckey]

        rows = []
        total = checked = 0
        for t in qs.iterator():
            total += 1
            stir = (t.stir or "").strip()
            pinfl = (t.leader_jshshir or "").strip()
            checked += 1

            # Faktura kaliti = STIR yoki PINFL (sync_factura_revenue bilan bir xil).
            factura_key = stir or pinfl

            # OKKM tin = STIR yoki PINFL->soliq TIN (sync_okkm_revenue bilan bir xil).
            # Faqat OKKM kerak bo'lganda resolve qilamiz (factura kanalida soliqqa bormaymiz).
            okkm_tin = None
            if channel in ("both", "okkm"):
                if stir:
                    okkm_tin = stir
                elif pinfl in tin_cache:
                    okkm_tin = tin_cache[pinfl]
                elif pinfl:
                    okkm_tin = _resolve_tin(t)
                    tin_cache[pinfl] = okkm_tin

            has_f = has_factura(factura_key) if factura_key else False
            has_o = has_okkm(okkm_tin) if okkm_tin else False

            if channel == "factura":
                if has_f:
                    continue
                reason = "faktura_yoq" if factura_key else "id_yoq"
            elif channel == "okkm":
                if has_o:
                    continue
                reason = "okkm_yoq" if okkm_tin else "tin_aniqlanmadi"
            else:  # both
                if not factura_key and not okkm_tin:
                    reason = "tin_aniqlanmadi"
                elif has_f or has_o:
                    continue
                else:
                    reason = "integratsiya_malumoti_yoq"

            rows.append({
                "tenant_id": t.pk,
                "name": t.name or t.leader_fio or "",
                "type": TYPE_LABEL.get(t.business_type, ""),
                "stir": stir,
                "pinfl": pinfl,
                "tin": (stir or okkm_tin or pinfl or ""),
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

        from collections import Counter
        reasons = Counter(r["reason"] for r in rows)
        uniq_ids = sorted({(r["stir"] or r["pinfl"]) for r in rows if (r["stir"] or r["pinfl"])})

        self.stdout.write(self.style.SUCCESS(
            f"Tekshirildi: {checked}/{total} tenant ({year}, channel={channel}). "
            f"Ro'yxatga tushdi: {len(rows)} "
            f"({', '.join(f'{k}={v}' for k, v in reasons.items()) or '-'})"
        ))
        self.stdout.write(f"Noyob STIR/PINFL: {len(uniq_ids)} ta")
        self.stdout.write(f"CSV: {out_path}\n")

        for r in rows:
            self.stdout.write(
                f"  {r['type']:6} STIR={r['stir'] or '-':12} PINFL={r['pinfl'] or '-':16} "
                f"{r['reason']:24} | {r['name']} | {r['shop']}"
            )
