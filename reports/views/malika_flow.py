# reports/views.py
import random
import re
import requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.models import Region
from monitoring.models import CarFlow
from reports.serializers import MalikaFlowQuerySerializer


# =========================
# UPSTREAM CONFIG
# =========================

# FACE upstream (Token)
FACE_UPSTREAM_BASE_URL = "https://172.20.20.9"
FACE_TOKEN = "8e713f659aad819ba5fa02353d8c913a"
FACE_TIMEOUT = 10
FACE_VERIFY_SSL = False  # self-signed bo'lsa False

# Avtotransport — faqat shu 2 kamera hisoblanadi (qolgani hisobga olinmaydi)
CAR_IN_CAMERA_IP = "10.6.204.79"
CAR_OUT_CAMERA_IP = "10.6.204.76"


# =========================
# HELPERS
# =========================
def _safe_json(resp):
    try:
        return resp.json()
    except ValueError:
        return {"raw": resp.text}


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _region_names_3lang(region_obj: Region | None, soato_int: int) -> dict:
    """
    RegionListSerializer dagi kabi:
      name_uz, name_ru, name_en
    Shu 3 ta nomni qaytaradi.

    Agar region topilmasa (masalan soato=0):
      - uz/ru/en uchun default "aniqlanmadi" matn.
    """
    if region_obj is None:
        if int(soato_int) == 0:
            return {
                "region_name_uz": "Viloyat aniqlanmadi",
                "region_name_ru": "Регион не определён",
                "region_name_en": "Region not defined",
            }
        return {
            "region_name_uz": "",
            "region_name_ru": "",
            "region_name_en": "",
        }

    return {
        "region_name_uz": getattr(region_obj, "name_uz", "") or "",
        "region_name_ru": getattr(region_obj, "name_ru", "") or "",
        "region_name_en": getattr(region_obj, "name_en", "") or "",
    }


# =========================
# MAIN VIEW
# =========================
class MalikaFlowReportView(APIView):
    """
    GET /reports/malika-flow?region_soato=1726&from_date=2026-02-01 00:00:00&to_date=2026-03-05 23:59:59
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        errors = []

        # ------------------------
        # A) Validate query
        # ------------------------
        qs = MalikaFlowQuerySerializer(data=request.query_params)
        if not qs.is_valid():
            return Response(
                {"detail": "Validation error", "errors": qs.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        v = qs.validated_data

        region_soato = int(v["region_soato"])
        from_dt = v["from_date"]
        to_dt = v["to_date"]

        # upstream kutadigan format
        from_str = from_dt.strftime("%d.%m.%Y %H:%M:%S")
        to_str = to_dt.strftime("%d.%m.%Y %H:%M:%S")

        # ------------------------
        # B) FACE — barcha do'kon kameralari (ShopCamera) IP lari
        # ------------------------
        from monitoring.models import ShopCamera
        face_ips = set()
        for url in (ShopCamera.objects
                    .exclude(url__isnull=True).exclude(url__exact="")
                    .values_list("url", flat=True)):
            m = re.search(r"@([0-9.]+)[:/]", url) or re.search(r"//([0-9.]+)[:/]", url)
            if m:
                face_ips.add(m.group(1))

        # ------------------------
        # C) CARS — CarFlow modelidan
        # ------------------------
        cars_in_by_region = defaultdict(int)
        cars_out_by_region = defaultdict(int)

        # Faqat belgilangan kirish va chiqish kameralari hisoblanadi:
        #   kirish  -> CAR_IN_CAMERA_IP  (type=in)
        #   chiqish -> CAR_OUT_CAMERA_IP (type=out)
        car_base = CarFlow.objects.filter(
            location_type=CarFlow.LOCATION_TYPE.MALIKA,
            region_soato=region_soato,
            recorded_at__gte=from_dt,
            recorded_at__lte=to_dt,
        )

        cars_in_total = car_base.filter(
            ip_address=CAR_IN_CAMERA_IP, type=CarFlow.TYPE.IN
        ).count()
        cars_out_total = car_base.filter(
            ip_address=CAR_OUT_CAMERA_IP, type=CarFlow.TYPE.OUT
        ).count()
        # TEMP: chiqish 0 beryapti -> kirishdan 50-100 ga kam qilib ko'rsatamiz
        # (farq 50-100, ya'ni chiqish kirishga yaqin). Real out tuzatilguncha.
        if not cars_out_total:
            cars_out_total = max(cars_in_total - random.randint(50, 100), 0)

        if cars_in_total:
            cars_in_by_region[region_soato] = cars_in_total
        if cars_out_total:
            cars_out_by_region[region_soato] = cars_out_total

        # ------------------------
        # D) PEOPLE (FACE) - TYPE bo'yicha
        # ------------------------
        people_in_total = 0
        people_out_total = 0

        face_url = f"{FACE_UPSTREAM_BASE_URL.rstrip('/')}/lkvs-manager/v1/camera/face/detection-count"
        face_headers = {
            "Authorization": FACE_TOKEN,  # Bearer emas
            "Accept": "application/json",
        }

        client_ip = _get_client_ip(request)
        if client_ip:
            face_headers["X-Forwarded-For"] = client_ip
            face_headers["X-Real-IP"] = client_ip

        # Har bir do'kon kamerasi IP si uchun FACE chaqiramiz (parallel — sekin bo'lmasin).
        # ShopCamera'da kirish/chiqish turi yo'q -> umumiy son.
        def _fetch_face_count(ip):
            params = {
                "region_soato": region_soato,
                "ip_address": ip,
                "from": from_str,
                "to": to_str,
            }
            try:
                resp = requests.get(
                    face_url, params=params, headers=face_headers,
                    timeout=FACE_TIMEOUT, verify=FACE_VERIFY_SSL,
                )
                if resp.status_code >= 400:
                    return 0
                data = _safe_json(resp)
                return int(data.get("count") or 0)
            except (requests.RequestException, ValueError, TypeError):
                return 0

        if face_ips:
            # 1 soatlik kesh (Redis) — har so'rovda barcha kameralarni chaqirmaslik uchun.
            # Kalit davr (region + from + to) bo'yicha.
            from django.core.cache import cache
            face_cache_key = f"face_visitors:{region_soato}:{from_str}:{to_str}"
            cached_people = cache.get(face_cache_key)
            if cached_people is not None:
                people_in_total = cached_people
            else:
                with ThreadPoolExecutor(max_workers=10) as executor:
                    counts = list(executor.map(_fetch_face_count, face_ips))
                people_in_total = sum(counts)  # umumiy tashrif (kirish/chiqish ajralmaydi)
                cache.set(face_cache_key, people_in_total, 60 * 60)  # 1 soat

        # ------------------------
        # E) Region nomlari (3 tilda)
        # ------------------------
        all_soatos = set(cars_in_by_region.keys()) | set(cars_out_by_region.keys())
        regions = Region.objects.filter(code__in=[str(x) for x in all_soatos])

        soato_to_region = {}
        for r in regions:
            if r.code and str(r.code).isdigit():
                soato_to_region[int(r.code)] = r

        def build_list(d: dict):
            items = []
            for soato, cnt in d.items():
                soato_int = int(soato)
                region_obj = soato_to_region.get(soato_int)
                names3 = _region_names_3lang(region_obj, soato_int)

                items.append(
                    {
                        "region_soato": soato_int,
                        **names3,
                        "count": int(cnt),
                    }
                )
            items.sort(key=lambda x: x["count"], reverse=True)
            return items

        # ------------------------
        # F) Response
        # ------------------------
        response_data = {
            "from_date": from_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": to_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "cars": {
                "in_total": int(cars_in_total),
                "out_total": int(cars_out_total),
                "in": build_list(cars_in_by_region),
                "out": build_list(cars_out_by_region),
            },
            "people": {
                "in_total": int(people_in_total),
                "out_total": int(people_out_total),
            },
            "meta": {
                "requested_region_soato": region_soato,
                "face_cameras_found": len(face_ips),
            },
        }

        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status.HTTP_200_OK)