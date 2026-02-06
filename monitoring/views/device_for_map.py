from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from directory.models import Region, District
from monitoring.models import Device
from monitoring.serializers_for_map import RegionStatsSerializer, DistrictStatsSerializer, DeviceSerializer

class RegionStatsAPIView(APIView):
    def get(self, request):
        regions = Region.objects.all()
        serializer = RegionStatsSerializer(regions, many=True)
        return Response(serializer.data)

class DistrictStatsAPIView(APIView):
    def get(self, request, region_id):
        districts = District.objects.all()
        serializer = DistrictStatsSerializer(districts, many=True)
        return Response(serializer.data)

class DeviceListAPIView(APIView):
    def get(self, request, region_id):
        devices = Device.objects.filter(region_id=region_id)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
