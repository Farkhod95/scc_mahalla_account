"""
YaTT soliq tushumi (company-account) NEGA kelmayotganini aniqlaydigan DIAGNOSTIKA.

Hech narsa yozmaydi (read-only) — faqat har bir YaTT uchun soliq zanjirini bosqichma-
bosqich chaqirib, qayerda uzilayotganini ko'rsatadi. soliq API faqat serverda ochilgani
uchun SHU buyruq ham serverda ishlatiladi.

    python manage.py diagnose_ytt_tax                 # barcha faol YaTT (default limit 25)
    python manage.py diagnose_ytt_tax --limit 0       # cheksiz (hammasi)
    python manage.py diagnose_ytt_tax --pinfl 1234... # bitta pinfl
    python manage.py diagnose_ytt_tax --include-inactive

Har YaTT uchun tekshiriladi:
  1) _resolve_tin       -> hozirgi sync qaysi tin bo'yicha so'rayapti (yoki None=skip)
  2) self-employment    -> pinfl dan tin chiqadimi (YaTT bu endpointda bormi)
  3) company-account    -> resolved tin bo'yicha payTax (hozirgi yo'l)
  4) company-account    -> PINFL TO'G'RIDAN-TO'G'RI bo'yicha payTax (faktura kabi)
  5) entrepreneur-rate  -> YaTT qat'iy/aylanma stavkasi (rate_summa)

Shu jadval orqali ko'rinadi: muammo (a) tin resolve bo'lmayaptimi, (b) company-account
STIR/tin bo'yicha 0 qaytaryaptimi-yu PINFL bo'yicha qaytaradimi.
"""
from __future__ import annotations

from datetime import date

import requests
from django.core.management.base import BaseCommand

from monitoring.models import ShopTenant
from monitoring.services import soliq_service
from monitoring.services.revenue_sync import _resolve_tin

# YaTT uchun ahamiyatli kodlar (Aylanma birinchi), keyin QQS/NDFL/Foyda solishtirish uchun.
PROBE_CODES = [(100, "Aylanma"), (46, "NDFL"), (1, "QQS"), (32, "Foyda")]


class Command(BaseCommand):
    help = "YaTT soliq tushumi nega kelmayotganini aniqlovchi diagnostika (read-only)."

    def add_arguments(self, parser):
        parser.add_argument("--pinfl", type=str, default=None, help="Faqat shu pinfl (leader_jshshir)")
        parser.add_argument("--limit", type=int, default=25, help="Nechta YaTT (0 = cheksiz)")
        parser.add_argument("--include-inactive", action="store_true", help="Nofaol YaTT larni ham")

    def handle(self, *args, **opts):
        today = date.today()
        ytd_from = f"01.01.{today.year}"
        today_str = today.strftime("%d.%m.%Y")

        qs = ShopTenant.objects.filter(business_type=ShopTenant.BusinessType.YTT)
        if opts.get("pinfl"):
            qs = qs.filter(leader_jshshir=opts["pinfl"].strip())
        if not opts.get("include_inactive"):
            qs = qs.exclude(activity_status=ShopTenant.ActivityStatus.INACTIVE)

        limit = opts.get("limit") or 0
        total = qs.count()
        self.stdout.write(f"YaTT topildi: {total} (limit={limit or 'cheksiz'}), davr {ytd_from}..{today_str}\n")

        # Sanoqchilar — xulosa uchun.
        n = 0
        no_stir = 0
        resolved_ok = 0
        se_has_tin = 0
        ca_resolved_nonzero = 0
        ca_pinfl_nonzero = 0
        rate_nonzero = 0

        for t in qs.iterator():
            if limit and n >= limit:
                break
            n += 1

            stir = (t.stir or "").strip()
            pinfl = (t.leader_jshshir or "").strip()
            if not stir:
                no_stir += 1

            self.stdout.write(self.style.MIGRATE_HEADING(
                f"\n[{n}] tenant#{t.pk} {t.name or ''} | stir={stir or '-'} pinfl={pinfl or '-'} status={t.activity_status}"
            ))

            # 1) hozirgi sync nima qiladi
            resolved = _resolve_tin(t)
            if resolved:
                resolved_ok += 1
            self.stdout.write(f"    _resolve_tin (sync ishlatadi) -> {resolved or 'None (SKIP — tax yozilmaydi)'}")

            # 2) self-employment: pinfl -> tin
            if pinfl:
                se = self._safe(lambda: soliq_service.get_self_employment(pinfl))
                if isinstance(se, dict):
                    se_tin = se.get("tin")
                    if se_tin:
                        se_has_tin += 1
                    self.stdout.write(f"    self-employment -> tin={se_tin or 'YOQ'}")
                else:
                    self.stdout.write(f"    self-employment -> {se}")

            # 3) company-account: resolved tin bo'yicha
            if resolved:
                got = self._probe_company(resolved, ytd_from, today_str)
                if got:
                    ca_resolved_nonzero += 1
                self.stdout.write(f"    company-account[resolved tin={resolved}] -> {self._fmt(got)}")

            # 4) company-account: PINFL to'g'ridan-to'g'ri (faktura kabi)
            if pinfl and pinfl != resolved:
                got_p = self._probe_company(pinfl, ytd_from, today_str)
                if got_p:
                    ca_pinfl_nonzero += 1
                self.stdout.write(f"    company-account[PINFL={pinfl}]     -> {self._fmt(got_p)}")

            # 5) entrepreneur activity rate (YaTT stavkasi)
            if pinfl:
                rates = self._safe(lambda: soliq_service.get_entrepreneur_activity_tax_rate(pinfl))
                if isinstance(rates, list) and rates:
                    summ = rates[0].get("rate_summa")
                    if summ:
                        rate_nonzero += 1
                    self.stdout.write(
                        f"    entrepreneur-rate -> firm={rates[0].get('firm_name')!r} "
                        f"rate_summa={summ} iestatus1={rates[0].get('iestatus1')}"
                    )
                else:
                    self.stdout.write(f"    entrepreneur-rate -> {rates}")

        self.stdout.write(self.style.SUCCESS(
            "\n==== XULOSA ====\n"
            f"  tekshirilgan YaTT:                 {n}\n"
            f"  STIR'siz (faqat pinfl):            {no_stir}\n"
            f"  _resolve_tin tin qaytardi:         {resolved_ok}  (qolgani SKIP — tax umuman yozilmaydi)\n"
            f"  self-employment tin berdi:         {se_has_tin}\n"
            f"  company-account[resolved]>0:       {ca_resolved_nonzero}\n"
            f"  company-account[PINFL]>0:          {ca_pinfl_nonzero}\n"
            f"  entrepreneur rate_summa>0:         {rate_nonzero}\n"
        ))

    def _probe_company(self, tin, period_from, period_to):
        """Har kod uchun payTax — {nom: payTax} (faqat noldan farqlilar uchun emas, hammasi)."""
        out = {}
        for code, name in PROBE_CODES:
            data = self._safe(
                lambda: soliq_service.get_company_account(tin, period_from, period_to, code)
            )
            if isinstance(data, dict):
                out[name] = data.get("payTax")
            else:
                out[name] = data  # xato matni
        return out

    @staticmethod
    def _fmt(probe):
        if not probe:
            return "—"
        parts = [f"{k}={v}" for k, v in probe.items()]
        nonzero = any(str(v) not in ("0", "0.0", "None", "") and not str(v).startswith("XATO")
                      for v in probe.values())
        flag = "  <== bor" if nonzero else "  (hammasi 0)"
        return ", ".join(parts) + flag

    @staticmethod
    def _safe(fn):
        """API chaqiruvini himoyalab chaqiradi — xato bo'lsa 'XATO: ...' string."""
        try:
            return fn()
        except (soliq_service.SoliqError, requests.RequestException) as e:
            return f"XATO: {e}"
