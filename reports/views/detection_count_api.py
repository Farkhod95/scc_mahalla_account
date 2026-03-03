import requests

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated  # xohlasangiz IsAuthenticated qiling
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.serializers import DetectionCountQuerySerializer


UPSTREAM_BASE_URL = "http://172.20.20.9:8853"  # http://IP:PORT
UPSTREAM_USERNAME = "safecity@2026"
UPSTREAM_PASSWORD = ">3LP391)KUa7"
UPSTREAM_TIMEOUT_SEC = 10


class DetectionCountProxyView(APIView):
    permission_classes = [IsAuthenticated]  # kerak bo‘lsa: [IsAuthenticated]

    def get(self, request):
        """
        Query parametrlarni tekshiradi:
        - ip_address: IP manzil
        - region_soato: butun son
        - from: sana va vaqt
        - to: sana va vaqt

        Sana formati: 25.02.2026 00:00:00
        """
        qs = DetectionCountQuerySerializer(
            data={
                "ip_address": request.query_params.get("ip_address"),
                "region_soato": request.query_params.get("region_soato"),
                "from_dt": request.query_params.get("from"),
                "to_dt": request.query_params.get("to"),
            }
        )
        qs.is_valid(raise_exception=True)
        v = qs.validated_data

        # Upstream aynan dd.mm.YYYY HH:MM:SS format kutyapti
        from_str = v["from_dt"].strftime("%d.%m.%Y %H:%M:%S")
        to_str = v["to_dt"].strftime("%d.%m.%Y %H:%M:%S")

        url = f"{UPSTREAM_BASE_URL.rstrip('/')}/detection-count"
        params = {
            "ip_address": str(v["ip_address"]),
            "region_soato": int(v["region_soato"]),
            "from": from_str,
            "to": to_str,
        }

        try:
            resp = requests.get(
                url,
                params=params,
                auth=(UPSTREAM_USERNAME, UPSTREAM_PASSWORD),
                timeout=UPSTREAM_TIMEOUT_SEC,
            )
        except requests.RequestException as e:
            return Response(
                {"detail": f"Upstream connect error: {e}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if resp.status_code == 401:
            return Response(
                {"detail": "Upstream auth failed (401)."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if resp.status_code >= 400:
            return Response(
                {"detail": f"Upstream error: {resp.status_code}", "body": resp.text[:1000]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # JSON bo‘lmasa ham raw qaytaramiz
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text}

        return Response(data, status=status.HTTP_200_OK)


