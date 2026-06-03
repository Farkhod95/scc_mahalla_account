"""
Do'kon kassa (NKM) rangi keshini oldindan to'ldiradi.

Bulk endpoint (/shop/cash-status/) birinchi marta sovuq keshda sekin
bo'lmasligi uchun (yoki cron). nkm_active 1 kun keshlanadi.

    python manage.py warm_shop_cash_status
"""
from django.core.management.base import BaseCommand

from monitoring.models import Shop
from monitoring.services.shop_status import shop_cash_status


class Command(BaseCommand):
    help = "Do'kon kassa (NKM) rangi keshini oldindan to'ldiradi."

    def handle(self, *args, **opts):
        shops = Shop.objects.prefetch_related("tenants").all()
        total = shops.count()
        self.stdout.write(f"Jami {total} ta do'kon...")
        counts = {"green": 0, "yellow": 0, "red": 0, "none": 0}
        for shop in shops:
            st = shop_cash_status(shop)
            counts[st["color"] or "none"] += 1
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: yashil={counts['green']}, sariq={counts['yellow']}, "
            f"qizil={counts['red']}, rangsiz={counts['none']}"
        ))
