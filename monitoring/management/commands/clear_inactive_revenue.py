"""
Berilgan tashkilot(lar)ning (tin/STIR bo'yicha) ESKI revenue datasini ikkala kunlik
jadvaldan o'chiradi: FacturaRevenueDaily (sync-factura-revenue-daily) va
OkkmRevenueDaily (sync-okkm-revenue-daily).

Sabab: sync nofaol ijarachini YANGILAMAYDI, lekin eski yozuvlari jadvalda qolib
ketadi. Bu command shu yozuvlarni ANIQ tin(lar) bo'yicha tozalaydi (sync logikasi
o'zgarmaydi).

Ishlatish:
    python manage.py clear_inactive_revenue 304529888 123456789           # DRY-RUN (sanaydi)
    python manage.py clear_inactive_revenue 304529888 123456789 --apply    # haqiqatan o'chiradi
"""
from django.core.management.base import BaseCommand, CommandError

from monitoring.models import ShopTenant, FacturaRevenueDaily, OkkmRevenueDaily


class Command(BaseCommand):
    help = "Berilgan tin(lar) bo'yicha eski revenue (factura + okkm) datasini o'chiradi."

    def add_arguments(self, parser):
        parser.add_argument("tins", nargs="+", help="O'chiriladigan tashkilot STIR(lar)i")
        parser.add_argument(
            "--apply", action="store_true",
            help="Haqiqatan o'chiradi (aks holda faqat ko'rsatadi — DRY-RUN).",
        )

    def handle(self, *args, **opts):
        tins = [t.strip() for t in opts["tins"] if t.strip()]
        if not tins:
            raise CommandError("Kamida bitta tin bering.")
        apply = opts.get("apply", False)

        total_f = total_o = 0
        for tin in tins:
            f_count = FacturaRevenueDaily.objects.filter(seller_tin=tin).count()
            o_count = OkkmRevenueDaily.objects.filter(tin=tin).count()
            total_f += f_count
            total_o += o_count

            # Qaysi ijarachi(lar)ga tegishli + holati — tasdiqlash uchun ko'rsatamiz.
            rows = list(
                ShopTenant.objects.filter(stir=tin).values_list("name", "activity_status")
            )
            info = ", ".join(f"{name} [{st}]" for name, st in rows) or "ijarachi topilmadi"
            self.stdout.write(f"tin={tin}: factura={f_count}, okkm={o_count}  ({info})")

            if any(st != ShopTenant.ActivityStatus.INACTIVE for _, st in rows):
                self.stdout.write(self.style.WARNING(
                    f"  DIQQAT: tin={tin} FAOL ijarachiga tegishli bo'lishi mumkin!"
                ))

        if not apply:
            self.stdout.write(self.style.WARNING(
                f"DRY-RUN — hech narsa o'chirilmadi (jami factura={total_f}, okkm={total_o}). "
                "O'chirish uchun: --apply"
            ))
            return

        f_deleted = FacturaRevenueDaily.objects.filter(seller_tin__in=tins).delete()[0]
        o_deleted = OkkmRevenueDaily.objects.filter(tin__in=tins).delete()[0]
        self.stdout.write(self.style.SUCCESS(
            f"O'chirildi: factura={f_deleted}, okkm={o_deleted}"
        ))
