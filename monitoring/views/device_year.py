from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from directory.models import Region
from monitoring.models import Device, DeviceYear, Object
from monitoring.serializers import DeviceYearCountSerializer


class RegionDeviceYearCountAPIView(APIView):
    def get(self, request):
        regions = Region.objects.all()
        device_years = DeviceYear.objects.all()

        response_data = []

        for region in regions:
            counts = (
                Device.objects.filter(region=region, device_year__isnull=False)
                .values('device_year_id')
                .annotate(count=Count('id'))
            )

            device_year_summary = []
            for entry in counts:
                dy = device_years.filter(id=entry['device_year_id']).first()
                if dy:
                    device_year_summary.append({
                        "device_year_id": dy.id,
                        "device_year_name": dy.name,
                        "count": entry['count']
                    })

            response_data.append({
                "id": region.id,
                "name": region.name,
                "center_x": region.center_x or "",
                "center_y": region.center_y or "",
                "zoom": region.zoom or "",
                "device_years": device_year_summary
            })
        # print(response_data)
        serializer = DeviceYearCountSerializer(response_data, many=True)
        return Response(response_data)


class ObjectDeviceYearCountAPIView(APIView):
    def get(self, request):
        regions = Region.objects.all()
        device_years = DeviceYear.objects.all()

        response_data = []

        for region in regions:
            counts = (
                Object.objects.filter(region=region, device_year__isnull=False)
                .values('device_year_id')
                .annotate(count=Count('id'))
            )

            device_year_summary = []
            for entry in counts:
                dy = device_years.filter(id=entry['device_year_id']).first()
                if dy:
                    device_year_summary.append({
                        "device_year_id": dy.id,
                        "device_year_name": dy.name,
                        "count": entry['count']
                    })

            response_data.append({
                "id": region.id,
                "name": region.name,
                "center_x": region.center_x or "",
                "center_y": region.center_y or "",
                "zoom": region.zoom or "",
                "device_years": device_year_summary
            })
        # print(response_data)
        serializer = DeviceYearCountSerializer(response_data, many=True)
        return Response(response_data)
