from rest_framework import serializers
from directory.models import District, Mahalla


class LocalDistrictMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "code", "name", "name_uz", "name_ru", "name_en", "is_active")


class LocalMahallaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mahalla
        fields = ("id", "code", "name", "name_uz", "name_ru", "name_en", "status", "is_active")


class GPSInspectorDistrictSerializer(serializers.Serializer):
    district_cad_code = serializers.CharField()
    region_cad_code = serializers.CharField()
    title = serializers.DictField()
    local_district = serializers.SerializerMethodField()

    def get_local_district(self, obj):
        district = District.objects.filter(code=str(obj.get("district_cad_code")), is_active=True).first()
        if district:
            return LocalDistrictMiniSerializer(district).data
        return None


class GPSInspectorMFYSerializer(serializers.Serializer):
    mfy_cad_code = serializers.CharField()
    district_cad_code = serializers.CharField()
    title = serializers.DictField()
    local_mahalla = serializers.SerializerMethodField()
    local_district = serializers.SerializerMethodField()

    def get_local_mahalla(self, obj):
        mahalla = Mahalla.objects.filter(code=str(obj.get("mfy_cad_code")), is_active=True).first()
        if mahalla:
            return LocalMahallaMiniSerializer(mahalla).data
        return None

    def get_local_district(self, obj):
        district = District.objects.filter(code=str(obj.get("district_cad_code")), is_active=True).first()
        if district:
            return LocalDistrictMiniSerializer(district).data
        return None


class GPSPointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class GPSInspectorItemSerializer(serializers.Serializer):
    pinfl = serializers.CharField()
    fullName = serializers.CharField()
    inspectorType = serializers.CharField()
    gps = GPSPointSerializer()
    dateTime = serializers.CharField()