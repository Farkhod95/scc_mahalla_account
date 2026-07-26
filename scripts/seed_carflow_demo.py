# Ishga tushirish:
#   python manage.py shell < scripts/seed_carflow_demo.py
# Docker orqali:
#   docker compose exec -T mahalla_account python manage.py shell < scripts/seed_carflow_demo.py
#
# Idempotent: har bir kun uchun avval o'sha kundagi eski demo yozuvlar
# o'chiriladi, keyin qayta yaratiladi — skript necha marta ishga tushirilsa
# ham (masalan yangi kunlar qo'shilganda) yozuvlar takrorlanib qolmaydi.

import random
from datetime import date, datetime, timedelta

from django.utils import timezone

from monitoring.models import BazarCamera, CarFlow

YEAR = 2026
MONTH = 7

# (kunlar oralig'i, har kunlik random son oralig'i) — kirish va chiqish soni
# har kun uchun bir xil random qiymatda (mashina kirdi = shu kuni chiqdi taxmini)
RANDOM_BATCHES = [
    (range(10, 21), (3000, 4000)),   # 10-20 iyul
    (range(22, 26), (2000, 3000)),   # 22-25 iyul
]

# Qat'iy son (in, out) — real/berilgan qiymatlar
FIXED_DAYS = {
    21: (200, 121),
    26: (1431, 1013),
}

# reports/views/malika_flow.py dagi filtrlash bilan bir xil bo'lishi uchun
# (aks holda yozuvlar Malika Flow hisobotida ko'rinmaydi)
LOCATION_TYPE = CarFlow.LOCATION_TYPE.MALIKA
REGION_SOATO = 1726
CAR_IN_CAMERA_IPS = ["10.6.204.79", "10.6.253.72"]
CAR_OUT_CAMERA_IPS = ["10.6.204.76", "10.6.253.72"]
ALL_CAR_IPS = list(set(CAR_IN_CAMERA_IPS + CAR_OUT_CAMERA_IPS))

cameras_by_ip = {
    cam.ip_address: cam
    for cam in BazarCamera.objects.filter(
        ip_address__in=ALL_CAR_IPS,
        location_type=LOCATION_TYPE,
    )
}

random_range_by_day = {}
for day_range, daily_range in RANDOM_BATCHES:
    for d in day_range:
        random_range_by_day[d] = daily_range

all_days = sorted(set(random_range_by_day) | set(FIXED_DAYS))


def random_time_on(day):
    seconds = random.randint(0, 24 * 3600 - 1)
    naive = datetime.combine(day, datetime.min.time()) + timedelta(seconds=seconds)
    return timezone.make_aware(naive)


def build_rows(day, count, flow_type, ip_pool):
    rows = []
    for _ in range(count):
        ip = random.choice(ip_pool)
        rows.append(CarFlow(
            camera=cameras_by_ip.get(ip),
            ip_address=ip,
            location_type=LOCATION_TYPE,
            region_soato=REGION_SOATO,
            type=flow_type,
            recorded_at=random_time_on(day),
        ))
    return rows


total_created = 0
for day_num in all_days:
    day = date(YEAR, MONTH, day_num)

    day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
    day_end = day_start + timedelta(days=1)
    CarFlow.objects.filter(
        ip_address__in=ALL_CAR_IPS,
        location_type=LOCATION_TYPE,
        region_soato=REGION_SOATO,
        recorded_at__gte=day_start,
        recorded_at__lt=day_end,
    ).delete()

    if day_num in FIXED_DAYS:
        in_count, out_count = FIXED_DAYS[day_num]
    else:
        in_count = random.randint(*random_range_by_day[day_num])
        out_count = in_count

    rows = build_rows(day, in_count, CarFlow.TYPE.IN, CAR_IN_CAMERA_IPS)
    rows += build_rows(day, out_count, CarFlow.TYPE.OUT, CAR_OUT_CAMERA_IPS)

    CarFlow.objects.bulk_create(rows, batch_size=1000)
    total_created += len(rows)
    print(f"{day}: kirish={in_count}, chiqish={out_count}")

print(f"JAMI yaratildi: {total_created} ta CarFlow yozuvi")
