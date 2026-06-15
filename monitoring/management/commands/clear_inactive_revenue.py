"""
Berilgan tashkilot(lar)ning (tin/STIR bo'yicha) ESKI revenue datasini kunlik
jadvallardan o'chiradi: FacturaRevenueDaily (sync-factura-revenue-daily) va/yoki
OkkmRevenueDaily (sync-okkm-revenue-daily).

Sabab: sync nofaol ijarachini YANGILAMAYDI, lekin eski yozuvlari jadvalda qolib
ketadi. Bu command shu yozuvlarni ANIQ tin(lar) bo'yicha tozalaydi (sync logikasi
o'zgarmaydi).

Ishlatish:
    python manage.py clear_inactive_revenue 304529888 123456789                 # DRY-RUN (ikkalasi)
    python manage.py clear_inactive_revenue 304529888 123456789 --apply          # ikkala jadvaldan o'chiradi
    python manage.py clear_inactive_revenue 304529888 --factura-only --apply      # faqat factura
    python manage.py clear_inactive_revenue 304529888 --okkm-only --apply         # faqat okkm
"""
from django.core.management.base import BaseCommand, CommandError

from monitoring.models import ShopTenant, FacturaRevenueDaily, OkkmRevenueDaily


class Command(BaseCommand):
    help = "Berilgan tin(lar) bo'yicha eski revenue (factura va/yoki okkm) datasini o'chiradi."

    def add_arguments(self, parser):
        parser.add_argument("tins", nargs="+", help="O'chiriladigan tashkilot STIR(lar)i")
        parser.add_argument(
            "--apply", action="store_true",
            help="Haqiqatan o'chiradi (aks holda faqat ko'rsatadi — DRY-RUN).",
        )
        parser.add_argument(
            "--factura-only", action="store_true",
            help="Faqat FacturaRevenueDaily ni o'chiradi.",
        )
        parser.add_argument(
            "--okkm-only", action="store_true",
            help="Faqat OkkmRevenueDaily ni o'chiradi.",
        )

    def handle(self, *args, **opts):
        tins = [t.strip() for t in opts["tins"] if t.strip()]
        if not tins:
            raise CommandError("Kamida bitta tin bering.")

        apply = opts.get("apply", False)
        factura_only = opts.get("factura_only", False)
        okkm_only = opts.get("okkm_only", False)
        if factura_only and okkm_only:
            raise CommandError("--factura-only va --okkm-only birga berilmaydi.")
        do_factura = not okkm_only
        do_okkm = not factura_only

        total_f = total_o = 0
        for tin in tins:
            parts = []
            if do_factura:
                f_count = FacturaRevenueDaily.objects.filter(seller_tin=tin).count()
                total_f += f_count
                parts.append(f"factura={f_count}")
            if do_okkm:
                o_count = OkkmRevenueDaily.objects.filter(tin=tin).count()
                total_o += o_count
                parts.append(f"okkm={o_count}")

            # Qaysi ijarachi(lar)ga tegishli + holati — tasdiqlash uchun ko'rsatamiz.
            rows = list(
                ShopTenant.objects.filter(stir=tin).values_list("name", "activity_status")
            )
            info = ", ".join(f"{name} [{st}]" for name, st in rows) or "ijarachi topilmadi"
            self.stdout.write(f"tin={tin}: {', '.join(parts)}  ({info})")

            if any(st != ShopTenant.ActivityStatus.INACTIVE for _, st in rows):
                self.stdout.write(self.style.WARNING(
                    f"  DIQQAT: tin={tin} FAOL ijarachiga tegishli bo'lishi mumkin!"
                ))

        if not apply:
            scope = []
            if do_factura:
                scope.append(f"factura={total_f}")
            if do_okkm:
                scope.append(f"okkm={total_o}")
            self.stdout.write(self.style.WARNING(
                f"DRY-RUN — hech narsa o'chirilmadi (jami {', '.join(scope)}). "
                "O'chirish uchun: --apply"
            ))
            return

        msg = []
        if do_factura:
            f_deleted = FacturaRevenueDaily.objects.filter(seller_tin__in=tins).delete()[0]
            msg.append(f"factura={f_deleted}")
        if do_okkm:
            o_deleted = OkkmRevenueDaily.objects.filter(tin__in=tins).delete()[0]
            msg.append(f"okkm={o_deleted}")
        self.stdout.write(self.style.SUCCESS(f"O'chirildi: {', '.join(msg)}"))
