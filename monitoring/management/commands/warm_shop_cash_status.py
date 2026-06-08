"""
Do'kon kassa (NKM) rangi keshini oldindan to'ldiradi.

Bulk endpoint (/shop/cash-status/) birinchi marta sovuq keshda sekin
bo'lmasligi uchun (yoki cron). nkm_active 1 kun keshlanadi.

    python manage.py warm_shop_cash_status
"""
from django.core.management.base import BaseCommand

from monitoring.tasks import warm_shop_cash_status_task


class Command(BaseCommand):
    help = "Do'kon kassa (NKM) rangi keshini oldindan to'ldiradi."

    def handle(self, *args, **opts):
        self.stdout.write("Kesh to'ldirilmoqda...")
        counts = warm_shop_cash_status_task()  # sinxron chaqiramiz (celery emas)
        self.stdout.write(self.style.SUCCESS(
            f"Tugadi: yashil={counts['green']}, sariq={counts['yellow']}, "
            f"qizil={counts['red']}, rangsiz={counts['none']}"
        ))
