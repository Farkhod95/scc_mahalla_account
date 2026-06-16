"""
Damafon (intercom) mikroservis PROXY view'lari.

Bizning auth (IsAuthenticated) ostida, so'rovni damafon mikroservisiga forward
qiladi. Ma'lumot mikroservis DB sida; bizda damafon modeli yo'q (faqat proxy).
Mahalla bo'yicha filtr: ?mahalla=<id> -> damafon.location_id == mahalla.id.
"""
import requests
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import DamafonCall
from monitoring.serializer.damafon import DamafonCallSerializer
from monitoring.services import damafon_service
from restapp.pagination import ResultsSetPagination


def _upstream_error(e):
    # Mikroservis javob bergan (4xx/5xx) bo'lsa — status va tanani o'tkazamiz.
    resp = getattr(e, "response", None)
    if resp is not None:
        try:
            body = resp.json()
        except ValueError:
            body = {"detail": resp.text}
        return Response(body, status=resp.status_code)
    # Ulanib bo'lmadi (timeout/connection) — 502.
    return Response(
        {"detail": f"Damafon xizmati bilan bog'lanib bo'lmadi: {e}"},
        status=status.HTTP_502_BAD_GATEWAY,
    )


class DamafonListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = damafon_service.list_damafons()
        except requests.RequestException as e:
            return _upstream_error(e)
        mahalla = request.query_params.get("mahalla")
        if mahalla:
            data = [d for d in data if str(d.get("location_id")) == str(mahalla)]
        return Response(data)

    def post(self, request):
        try:
            data = damafon_service.create_damafon(request.data)
        except requests.RequestException as e:
            return _upstream_error(e)
        return Response(data, status=status.HTTP_201_CREATED)


class DamafonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            return Response(damafon_service.get_damafon(pk))
        except requests.RequestException as e:
            return _upstream_error(e)

    def put(self, request, pk):
        try:
            return Response(damafon_service.update_damafon(pk, request.data))
        except requests.RequestException as e:
            return _upstream_error(e)

    def delete(self, request, pk):
        try:
            damafon_service.delete_damafon(pk)
        except requests.RequestException as e:
            return _upstream_error(e)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DamafonSnapshotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            content, content_type = damafon_service.snapshot(pk)
        except requests.RequestException as e:
            return _upstream_error(e)
        return HttpResponse(content, content_type=content_type)


class DamafonWebrtcView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        damafon_id = request.query_params.get("damafon_id")
        if not damafon_id:
            return Response({"detail": "damafon_id majburiy"}, status=status.HTTP_400_BAD_REQUEST)
        offer = request.body.decode("utf-8", "ignore")  # brauzer SDP offer (text/plain)
        try:
            answer = damafon_service.webrtc(damafon_id, offer)
        except requests.RequestException as e:
            return _upstream_error(e)
        return HttpResponse(answer, content_type="text/plain")


class DamafonDoorbellView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            return Response(damafon_service.doorbell(request.data))
        except requests.RequestException as e:
            return _upstream_error(e)


class DamafonCallListView(ListAPIView):
    """
    Damafon qo'ng'iroqlari TARIXI (bizning DB dan) — damafon_listener yozadi.
    ?mahalla=<id> bo'yicha filtr (location_id). Sahifalash: ?limit=. Eng yangisi birinchi.
    """
    serializer_class = DamafonCallSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = DamafonCall.objects.all()
        mahalla = self.request.query_params.get("mahalla")
        if mahalla:
            qs = qs.filter(location_id=mahalla)
        return qs
