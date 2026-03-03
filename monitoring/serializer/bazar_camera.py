from rest_framework import serializers

from directory.serializers import RegionListSerializer, DistrictListSerializer, MahallaListSerializer
from monitoring.models import BazarCamera


class BazarCameraSerializer(serializers.ModelSerializer):

    class Meta:
        model = BazarCamera
        fields = ('id', 'object_name', 'type', 'ip_address', 'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol', 'region', 'district', 'mahalla')


class BazarCameraListSerializer(serializers.ModelSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = BazarCamera
        fields = ('id', 'object_name', 'type', 'ip_address', 'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol', 'region', 'region_detail', 'district', 'district_detail', 'mahalla', 'mahalla_detail')