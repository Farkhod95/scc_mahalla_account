from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from monitoring.models import Device


class DeviceYearSummaryAPIView(APIView):
    def get(self, request):
        region_id = request.query_params.get('region_id')

        queryset = Device.objects.filter(device_year__isnull=False)
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        grouped = (
            queryset
            .values('device_year_id', 'device_year__name', 'device_year__color')
            .annotate(count=Count('id'))  # har bir yilda nechta qurilma borligini sanaydi
            .order_by('device_year_id')
        )

        result = []
        for item in grouped:
            result.append({
                "device_year_id": item["device_year_id"],
                "device_year_name": item["device_year__name"],
                "device_year_color": item["device_year__color"],
                "count": item["count"],
            })

        return Response(result)
