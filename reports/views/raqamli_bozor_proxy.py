# reports/views/raqamli_bozor_proxy.py
import os

import requests
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Raqamli bozor (scc_raqamli_bozor) upstream — statik token orqali (X-Api-Key).
# Token faqat environment orqali beriladi (kodga hardcode qilinmaydi).
RAQAMLI_BOZOR_BASE_URL = os.environ.get("RAQAMLI_BOZOR_BASE_URL", "http://192.168.168.171:3000")
RAQAMLI_BOZOR_STATIC_TOKEN = os.environ.get("RAQAMLI_BOZOR_STATIC_TOKEN", "")
RAQAMLI_BOZOR_TIMEOUT = 15


class RaqamliBozorProxyView(APIView):
    """
    Raqamli bozor API'siga statik token bilan to'liq proxy (GET/POST/PUT/PATCH/DELETE).

    /reports/raqamli-bozor/<endpoint>?...  ->
        {RAQAMLI_BOZOR_BASE_URL}/api/v1/<endpoint>?...

    Statik token faqat backend-backend orasida ishlatiladi, frontendga chiqmaydi —
    Malika bozorga login qilgan (IsAuthenticated) foydalanuvchi shu orqali
    raqamli_bozor'dagi istalgan (mavjud) API resursini o'qiy va o'zgartira oladi.
    So'rov tanasi (JSON yoki multipart, fayllar bilan) o'zgartirilmay, xuddi
    shu Content-Type bilan upstream'ga uzatiladi.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, endpoint):
        return self._proxy(request, endpoint, "GET")

    def post(self, request, endpoint):
        return self._proxy(request, endpoint, "POST")

    def put(self, request, endpoint):
        return self._proxy(request, endpoint, "PUT")

    def patch(self, request, endpoint):
        return self._proxy(request, endpoint, "PATCH")

    def delete(self, request, endpoint):
        return self._proxy(request, endpoint, "DELETE")

    def _proxy(self, request, endpoint, method):
        if not RAQAMLI_BOZOR_STATIC_TOKEN:
            return Response(
                {"detail": "Backendda RAQAMLI_BOZOR_STATIC_TOKEN sozlanmagan."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        url = f"{RAQAMLI_BOZOR_BASE_URL.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
        headers = {
            "X-Api-Key": RAQAMLI_BOZOR_STATIC_TOKEN,
            "Accept": "application/json",
        }
        if request.content_type:
            headers["Content-Type"] = request.content_type

        # Tana o'qilmasdan avval (request.data/.FILES ga tegilmagan) xom bytes
        # sifatida olinadi — shu bois JSON ham, multipart (fayl) ham xuddi
        # kelgan holicha, boundary'si bilan uzatiladi.
        body = request.body if request.body else None

        try:
            resp = requests.request(
                method,
                url,
                params=request.query_params,
                data=body,
                headers=headers,
                timeout=RAQAMLI_BOZOR_TIMEOUT,
            )
        except requests.RequestException as e:
            return Response(
                {"detail": f"Upstream connection error: {e}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "application/json" in content_type:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}
        else:
            payload = {"raw": resp.text}

        return Response(payload, status=resp.status_code)
