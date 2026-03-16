# reports/views.py
import requests
from collections import defaultdict
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.models import Region
from monitoring.models import BazarCamera
from reports.serializers import MalikaFlowQuerySerializer


# =========================
# UPSTREAM CONFIG
# =========================

# DRB upstream (Basic Auth)
DRB_UPSTREAM_BASE_URL = "http://172.20.20.9:8853"
DRB_UPSTREAM_USERNAME = "safecity@2026"
DRB_UPSTREAM_PASSWORD = ">3LP391)KUa7"
DRB_TIMEOUT = 10

# FACE upstream (Token)
FACE_UPSTREAM_BASE_URL = "https://172.20.20.9"
FACE_TOKEN = "8e713f659aad819ba5fa02353d8c913a"
FACE_TIMEOUT = 10
FACE_VERIFY_SSL = False  # self-signed bo‘lsa False


# =========================
# HELPERS
# =========================
def _safe_json(resp):
    try:
        return resp.json()
    except ValueError:
        return {"raw": resp.text}


def _clip(text: str, n: int = 1200) -> str:
    if text is None:
        return ""
    return str(text)[:n]


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
class CenterOfCivilizationReportView(APIView):
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
        # B) Kameralarni topish (logika o‘zgarmaydi)
        # ------------------------
        cameras = (
            BazarCamera.objects.filter(is_active=True, location_type='civilization')
            .exclude(ip_address__isnull=True)
            .exclude(ip_address="")
        )

        total_cams = cameras.count()
        drb_cams = cameras.filter(camera_type=BazarCamera.CAMERA_TYPE.DRB)
        face_cams = cameras.filter(camera_type=BazarCamera.CAMERA_TYPE.FACE)

        if total_cams == 0:
            errors.append(
                {
                    "source": "db",
                    "error": "No active cameras found for this region_soato",
                    "region_soato": region_soato,
                    "hint": "BazarCamera.region (code yoki id) region_soato ga mosligini tekshiring, is_active=True bo‘lsin",
                }
            )

        # ------------------------
        # C) CARS (DRB) - TYPE bo‘yicha QAT’IY:
        #    INPUT -> entry
        #    OUTPUT -> exit
        #    (fallback yo‘q)
        # ------------------------
        cars_in_by_region = defaultdict(int)
        cars_out_by_region = defaultdict(int)
        cars_in_total = 0
        cars_out_total = 0

        drb_url = f"{DRB_UPSTREAM_BASE_URL.rstrip('/')}/detection-count"

        for cam in drb_cams:
            params = {
                "ip_address": str(cam.ip_address),
                "region_soato": region_soato,
                "from": from_str,
                "to": to_str,
            }

            try:
                resp = requests.get(
                    drb_url,
                    params=params,
                    auth=(DRB_UPSTREAM_USERNAME, DRB_UPSTREAM_PASSWORD),
                    timeout=DRB_TIMEOUT,
                )
            except requests.RequestException as e:
                errors.append(
                    {
                        "source": "drb",
                        "ip_address": cam.ip_address,
                        "camera_type": "drb",
                        "type": cam.type,
                        "error": "Upstream connection error",
                        "message": str(e),
                    }
                )
                continue

            if resp.status_code >= 400:
                errors.append(
                    {
                        "source": "drb",
                        "ip_address": cam.ip_address,
                        "camera_type": "drb",
                        "type": cam.type,
                        "status_code": resp.status_code,
                        "body": _clip(resp.text),
                    }
                )
                continue

            data = _safe_json(resp)
            region_block = data.get("region")

            # DRB response:
            # {"total":..., "entry":..., "exit":..., "region": {"1726":{"entry":313,"exit":0}, ...}}
            if isinstance(region_block, dict):
                for soato_key, val in region_block.items():
                    try:
                        soato_int = int(soato_key)
                    except Exception:
                        continue

                    entry = 0
                    exit_ = 0
                    if isinstance(val, dict):
                        try:
                            entry = int(val.get("entry") or 0)
                        except Exception:
                            entry = 0
                        try:
                            exit_ = int(val.get("exit") or 0)
                        except Exception:
                            exit_ = 0

                    # ✅ QAT’IY taqsim:
                    # if cam.type == BazarCamera.TYPE.INPUT:
                    #     cars_in_by_region[soato_int] += entry
                    #     cars_in_total += entry
                    # elif cam.type == BazarCamera.TYPE.OUTPUT:
                    #     cars_out_by_region[soato_int] += exit_
                    #     cars_out_total += exit_

                    cars_in_by_region[soato_int] += entry
                    cars_out_by_region[soato_int] += exit_

                    cars_in_total += entry
                    cars_out_total += exit_

                continue

            # fallback: agar region yo‘q bo‘lsa (bu holda ham TYPE bo‘yicha bitta tomonga qo‘shamiz)
            count_val = data.get("count", data.get("total", 0))
            try:
                count_val = int(count_val or 0)
            except Exception:
                count_val = 0

            # if cam.type == BazarCamera.TYPE.INPUT:
            #     cars_in_total += count_val
            #     cars_in_by_region[region_soato] += count_val
            # elif cam.type == BazarCamera.TYPE.OUTPUT:
            #     cars_out_total += count_val
            #     cars_out_by_region[region_soato] += count_val
            cars_in_total += count_val
            cars_out_total += count_val

            cars_in_by_region[region_soato] += count_val
            cars_out_by_region[region_soato] += count_val

        # ------------------------
        # D) PEOPLE (FACE) - TYPE bo‘yicha
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

        for cam in face_cams:
            params = {
                "region_soato": region_soato,
                "ip_address": str(cam.ip_address),
                "from": from_str,
                "to": to_str,
            }

            try:
                resp = requests.get(
                    face_url,
                    params=params,
                    headers=face_headers,
                    timeout=FACE_TIMEOUT,
                    verify=FACE_VERIFY_SSL,
                )
            except requests.RequestException as e:
                errors.append(
                    {
                        "source": "face",
                        "ip_address": cam.ip_address,
                        "camera_type": "face",
                        "type": cam.type,
                        "error": "Upstream connection error",
                        "message": str(e),
                    }
                )
                continue

            if resp.status_code >= 400:
                errors.append(
                    {
                        "source": "face",
                        "ip_address": cam.ip_address,
                        "camera_type": "face",
                        "type": cam.type,
                        "status_code": resp.status_code,
                        "body": _safe_json(resp),
                    }
                )
                continue

            data = _safe_json(resp)
            try:
                count_val = int(data.get("count") or 0)
            except Exception:
                count_val = 0

            if cam.type == BazarCamera.TYPE.INPUT:
                people_in_total += count_val
            elif cam.type == BazarCamera.TYPE.OUTPUT:
                people_out_total += count_val

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
                "cameras_found": total_cams,
                "drb_cameras_found": drb_cams.count(),
                "face_cameras_found": face_cams.count(),
            },
        }

        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status.HTTP_200_OK)