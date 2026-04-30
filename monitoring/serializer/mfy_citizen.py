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
    avatar = serializers.SerializerMethodField()

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

    def get_avatar(self, obj):
        if not obj.avatar:
            return None

        request = self.context.get('request')
        if not request:
            # request bo'lmasa ham kamida fayl url qaytadi
            return obj.avatar.url

        url = request.build_absolute_uri(obj.avatar.url)

        # Agar build_absolute_uri http qilib bersa, majburan https ga o'tkazamiz
        # (Ko'p holatda reverse proxy/ssl terminator sabab bo'ladi)
        return url.replace('http://', 'http://', 1)