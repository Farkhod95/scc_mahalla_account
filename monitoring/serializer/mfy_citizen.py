from rest_framework import serializers
from directory.serializers import RegionListSerializer, DistrictListSerializer, MahallaListSerializer, GomSerializer
from monitoring.models import MFYCitizen


class MFYCitizenSerializer(serializers.ModelSerializer):

    class Meta:
        model = MFYCitizen
        fields = (
            'id', 'full_name', 'category', 'address', 'phone', 'avatar',
            'degree', 'type', 'coordinate_x', 'coordinate_y',
            'region', 'district', 'gom', 'mahalla',
            'is_active'
        )


class MFYCitizenListSerializer(serializers.ModelSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    gom_detail = GomSerializer(source='gom', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = MFYCitizen
        fields = (
            'id', 'full_name', 'category', 'address', 'phone', 'avatar',
            'degree', 'type', 'coordinate_x', 'coordinate_y',
            'region', 'region_detail',
            'district', 'district_detail',
            'gom', 'gom_detail',
            'mahalla', 'mahalla_detail',
            'is_active'
        )