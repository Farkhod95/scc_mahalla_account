import requests

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.serializers import FaceDetectionCountQuerySerializer

UPSTREAM_BASE_URL = "https://172.20.20.9"

# Backend ichida saqlanadigan token (frontend yubormaydi)
DEFAULT_BEARER_TOKEN = "8e713f659aad819ba5fa02353d8c913a"

# Timeout (sekund)
UPSTREAM_TIMEOUT = 10


class FaceDetectionCountProxyView(APIView):
    """
    Frontend yuboradi:
      region_soato=10
      ip_address=192.168.11.105
      from=26.02.2026 00:00:00
      to=26.02.2026 23:59:59

    Sana formati: dd.mm.YYYY HH:MM:SS
    """
    permission_classes = [IsAuthenticated]  # xohlasangiz keyin auth qo'shasiz

    def get(self, request):
        # ---------------------------------------
        # A) Token bor-yo'qligini tekshiramiz
        # ---------------------------------------
        if not DEFAULT_BEARER_TOKEN or DEFAULT_BEARER_TOKEN == "PASTE_YOUR_TOKEN_HERE":
            return Response(
                {"detail": "Backendda DEFAULT_BEARER_TOKEN qo'yilmagan."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ---------------------------------------
        # B) Query params validatsiya
        # ---------------------------------------
        s = FaceDetectionCountQuerySerializer(
            data={
                "region_id": request.query_params.get("region_soato"),
                "ip_address": request.query_params.get("ip_address"),
                "from_dt": request.query_params.get("from"),
                "to_dt": request.query_params.get("to"),
            }
        )
        s.is_valid(raise_exception=True)
        v = s.validated_data

        # ---------------------------------------
        # C) Sana formatini upstream kutgan ko'rinishga qaytaramiz
        # ---------------------------------------
        from_str = v["from_dt"].strftime("%d.%m.%Y %H:%M:%S")
        to_str = v["to_dt"].strftime("%d.%m.%Y %H:%M:%S")

        # ---------------------------------------
        # D) Upstream URL va params
        # ---------------------------------------
        upstream_url = f"{UPSTREAM_BASE_URL.rstrip('/')}/lkvs-manager/v1/camera/face/detection-count"
        params = {
            "region_id": int(v["region_id"]),
            "ip_address": str(v["ip_address"]),
            "from": from_str,
            "to": to_str,
        }

        # ---------------------------------------
        # E) Headerga tokenni backend o'zi qo'yadi
        # ---------------------------------------
        headers = {
            "Authorization": f"Bearer {DEFAULT_BEARER_TOKEN}",
            "Accept": "application/json",
        }

        # ---------------------------------------
        # F) Upstreamga so'rov
        # ---------------------------------------
        try:
            resp = requests.get(upstream_url, params=params, headers=headers, timeout=UPSTREAM_TIMEOUT)
        except requests.RequestException as e:
            return Response(
                {"detail": f"Upstream connection error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # ---------------------------------------
        # G) Upstream xatolarini qayta ishlash
        # ---------------------------------------
        if resp.status_code in (401, 403):
            return Response(
                {"detail": "Upstream authorization failed (token yaroqsiz/eskirgan).", "body": resp.text[:500]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if resp.status_code >= 400:
            return Response(
                {"detail": f"Upstream error: {resp.status_code}", "body": resp.text[:1000]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # ---------------------------------------
        # H) JSON yoki raw qaytarish
        # ---------------------------------------
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text}

        return Response(data, status=status.HTTP_200_OK)
