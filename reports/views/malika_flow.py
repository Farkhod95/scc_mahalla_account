import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import path


UPSTREAM_URL = "http://172.20.20.9:8853/detection-count"

LOGIN = "safecity@2026"
PASSWORD = ">3LP391)KUa7"


class MalikaFlowProxy(APIView):
    """
    GET /reports/malika-flow?from_date=...&end_date=...

    Bu API:
    - parametrlani oladi
    - upstream service ga yuboradi
    - kelgan javobni o'zgartirmasdan qaytaradi
    """

    authentication_classes = []   # agar auth kerak bo'lmasa
    permission_classes = []

    def get(self, request):

        from_date = request.GET.get("from_date")
        end_date = request.GET.get("end_date")

        if not from_date or not end_date:
            return Response(
                {"error": "from_date va end_date majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = requests.get(
                UPSTREAM_URL,
                params={
                    "from_date": from_date,
                    "end_date": end_date
                },
                auth=(LOGIN, PASSWORD),
                timeout=30
            )

            # upstream json ni o'zgarishsiz qaytaramiz
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
