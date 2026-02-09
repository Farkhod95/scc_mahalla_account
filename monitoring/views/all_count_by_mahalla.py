# monitoring/views/import_by_mahalla_id.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from monitoring.models import CameraInformation, MahallaCrime, Object, Employee


class AllCountByMahallaView(APIView):
    """
    GET/POST:
      - mahalla_id berilsa: shu mahallaga tegishli sonlar
      - mahalla_id berilmasa: umumiy (hammasi) sonlar

    Misol:
      GET  /api/v1/camera-information/fields/import-by-mahalla-id/?mahalla_id=12
      POST /api/v1/camera-information/fields/import-by-mahalla-id/  { "mahalla_id": 12 }
    """

    def _get_mahalla_id(self, request):
        # 1) query param: ?mahalla_id=12
        mahalla_id = request.query_params.get("mahalla_id")

        # 2) POST body: {"mahalla_id": 12}
        if mahalla_id is None:
            mahalla_id = request.data.get("mahalla_id")

        if mahalla_id in (None, "", "null"):
            return None

        try:
            return int(mahalla_id)
        except (TypeError, ValueError):
            return "INVALID"

    def _build_counts(self, mahalla_id=None):
        # Base querysetlar
        employee_qs = Employee.objects.all()
        object_qs = Object.objects.all()
        crime_qs = MahallaCrime.objects.all()
        camera_qs = CameraInformation.objects.all()

        # Filter: faqat mahalla_id berilganda
        if mahalla_id is not None:
            employee_qs = employee_qs.filter(mahalla_id=mahalla_id)
            object_qs = object_qs.filter(mahalla_id=mahalla_id)
            crime_qs = crime_qs.filter(mahalla_id=mahalla_id)
            camera_qs = camera_qs.filter(mahalla_id=mahalla_id)

        # Natija
        return {
            "employee_count": employee_qs.count(),
            "object_count": object_qs.count(),
            "mahalla_crime_count": crime_qs.count(),
            "camera_information_count": camera_qs.count(),
        }

    def get(self, request, *args, **kwargs):
        mahalla_id = self._get_mahalla_id(request)

        if mahalla_id == "INVALID":
            return Response(
                {"detail": "mahalla_id noto‘g‘ri. Integer bo‘lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            "mahalla_id": mahalla_id,  # None bo‘lsa ham qaytadi
            "counts": self._build_counts(mahalla_id=mahalla_id),
        }
        return Response(data, status=status.HTTP_200_OK)

    # def post(self, request, *args, **kwargs):
    #     # POST ham GET bilan bir xil ishlasin
    #     return self.get(request, *args, **kwargs)
