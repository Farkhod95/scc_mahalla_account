# Ishga tushirish:
#   python manage.py shell < scripts/seed_carflow_demo.py
# Docker orqali:
#   docker compose exec -T mahalla_account python manage.py shell < scripts/seed_carflow_demo.py

import random
from datetime import date, datetime, timedelta

from django.utils import timezone

from monitoring.models import BazarCamera, CarFlow

YEAR = 2026
MONTH = 7

# 10-20 iyul: kunlik random(3000, 4000) kirish, shuncha ham chiqish
RANDOM_RANGE_DAYS = range(10, 21)
DAILY_RANGE = (3000, 4000)

# 21 iyul: qat'iy son
FIXED_DAYS = {21: (200, 121)}

# reports/views/malika_flow.py dagi filtrlash bilan bir xil bo'lishi uchun
# (aks holda yozuvlar Malika Flow hisobotida ko'rinmaydi)
LOCATION_TYPE = CarFlow.LOCATION_TYPE.MALIKA
REGION_SOATO = 1726
CAR_IN_CAMERA_IPS = ["10.6.204.79", "10.6.253.72"]
CAR_OUT_CAMERA_IPS = ["10.6.204.76", "10.6.253.72"]

cameras_by_ip = {
    cam.ip_address: cam
    for cam in BazarCamera.objects.filter(
        ip_address__in=set(CAR_IN_CAMERA_IPS + CAR_OUT_CAMERA_IPS),
        location_type=LOCATION_TYPE,
    )
}


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


days = {d: None for d in RANDOM_RANGE_DAYS}
days.update(FIXED_DAYS)

total_created = 0
for day_num in sorted(days):
    day = date(YEAR, MONTH, day_num)

    if days[day_num] is not None:
        in_count, out_count = days[day_num]
    else:
        in_count = random.randint(*DAILY_RANGE)
        out_count = in_count

    rows = build_rows(day, in_count, CarFlow.TYPE.IN, CAR_IN_CAMERA_IPS)
    rows += build_rows(day, out_count, CarFlow.TYPE.OUT, CAR_OUT_CAMERA_IPS)

    CarFlow.objects.bulk_create(rows, batch_size=1000)
    total_created += len(rows)
    print(f"{day}: kirish={in_count}, chiqish={out_count}")

print(f"JAMI yaratildi: {total_created} ta CarFlow yozuvi")
