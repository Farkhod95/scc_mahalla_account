import requests

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.serializers import FaceDetectionCountQuerySerializer

UPSTREAM_BASE_URL = "https://172.20.20.9"
DEFAULT_TOKEN = "8e713f659aad819ba5fa02353d8c913a"
UPSTREAM_TIMEOUT = 10
UPSTREAM_VERIFY_SSL = False  # self-signed bo‘lsa False


class FaceDetectionCountProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not DEFAULT_TOKEN:
            return Response(
                {"detail": "Backendda DEFAULT_TOKEN qo‘yilmagan."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 1) Validate (sizning serializer fieldlaringizga mos)
        s = FaceDetectionCountQuerySerializer(
            data={
                "region_soato": request.query_params.get("region_soato"),
                "ip_address": request.query_params.get("ip_address"),
                "from_dt": request.query_params.get("from"),
                "to_dt": request.query_params.get("to"),
            }
        )
        s.is_valid(raise_exception=True)
        v = s.validated_data

        # 2) datetime -> dd.mm.YYYY HH:MM:SS
        from_str = v["from_dt"].strftime("%d.%m.%Y %H:%M:%S")
        to_str = v["to_dt"].strftime("%d.%m.%Y %H:%M:%S")

        upstream_url = f"{UPSTREAM_BASE_URL.rstrip('/')}/lkvs-manager/v1/camera/face/detection-count"

        # ⚠️ Agar upstream haqiqatan region_id kutsa:
        # params = {"region_id": int(v["region_soato"]), ...}
        # Agar upstream region_soato kutsa (sizda shunday deb yozilgan):
        params = {
            "region_id": int(v["region_soato"]),  # ✅ ko‘pincha upstream shu nomni kutadi
            "ip_address": str(v["ip_address"]),
            "from": from_str,
            "to": to_str,
        }

        headers = {
            "Authorization": DEFAULT_TOKEN,  # ✅ Bearer emas (Postman’dagi kabi)
            "Accept": "application/json",
        }

        # ixtiyoriy: lang
        lang = request.headers.get("lang") or request.headers.get("Lang")
        if lang:
            headers["lang"] = lang

        # client IP ni uzatib ko‘ramiz (upstream qo‘llasa)
        client_ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR")
        )
        if client_ip:
            headers["X-Forwarded-For"] = client_ip
            headers["X-Real-IP"] = client_ip

        # 3) Request
        try:
            resp = requests.get(
                upstream_url,
                params=params,
                headers=headers,
                timeout=UPSTREAM_TIMEOUT,
                verify=UPSTREAM_VERIFY_SSL,
            )
        except requests.RequestException as e:
            return Response(
                {"detail": f"Upstream connection error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # 4) MUHIM: Upstream status + body’ni o‘zgartirmay qaytaramiz
        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "application/json" in content_type:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}
        else:
            payload = {"raw": resp.text}

        return Response(payload, status=resp.status_code)