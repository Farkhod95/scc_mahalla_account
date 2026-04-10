from rest_framework import serializers

from .models import Region, District, Mahalla, Organization, Department, Position, Gom


class LocaleSerializer(serializers.ModelSerializer):
    name_uz = serializers.CharField(allow_blank=False)
    name_ru = serializers.CharField(allow_blank=False)
    name_en = serializers.CharField(allow_blank=False)


class RelatedRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class RelatedDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class RelatedPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class RegionSerializer(LocaleSerializer):
    class Meta:
        model = Region
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'center_x', 'center_y', 'zoom')
        extra_kwargs = {
            'name_en': {"required": True},
            'name_ru': {"required": True},
            'name_uz': {"required": True},
            'code': {"required": True},
        }


class RegionListSerializer(LocaleSerializer):
    class Meta:
        model = Region
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'center_x', 'center_y', 'zoom')


class DistrictListSerializer(LocaleSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)

    class Meta:
        model = District
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'region_detail', 'center_x',
                  'center_y', 'zoom')


class DistrictSerializer(LocaleSerializer):
    class Meta:
        model = District
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'center_x', 'center_y', 'zoom')
        extra_kwargs = {
            'name_uz': {"required": True},
            'name_ru': {"required": True},
            'name_en': {"required": True},
            'region': {"required": True},
            'code': {"required": True},
        }


class GomListSerializer(LocaleSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)

    class Meta:
        model = Gom
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'region_detail', 'district',
                  'district_detail')


class GomSerializer(LocaleSerializer):
    class Meta:
        model = Gom
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'district')
        extra_kwargs = {
            'name_uz': {"required": True},
            'name_ru': {"required": True},
            'name_en': {"required": True},
            'district': {"required": True},
            'code': {"required": True},
        }


class MahallaListSerializer(LocaleSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)

    class Meta:
        model = Mahalla
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'region_detail', 'district',
                  'district_detail', 'center_x', 'center_y', 'zoom')


class MahallaSerializer(LocaleSerializer):
    class Meta:
        model = Mahalla
        fields = ('id', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'district', 'center_x', 'center_y', 'zoom')
        extra_kwargs = {
            'name_uz': {"required": True},
            'name_ru': {"required": True},
            'name_en': {"required": True},
            'district': {"required": True},
            'code': {"required": True},
        }
        
        

class OrganizationSerializer(LocaleSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'number', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region',
                  'district')
        extra_kwargs = {
            'code': {"required": True},
            'name_uz': {"required": True},
            'name_en': {"required": True},
            'name_ru': {"required": True},
        }


class OrganizationListSerializer(LocaleSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaSerializer(source='mahalla', read_only=True)

    class Meta:
        model = Organization
        fields = ('id', 'number', 'code', 'name', 'name_uz', 'name_ru', 'name_en', 'region', 'region_detail',
                  'district', 'district_detail', 'mahalla', 'mahalla_detail')


class OrganizationListPublicSerializer(LocaleSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'number', 'code')


class DepartmentSerializer(LocaleSerializer):
    class Meta:
        model = Department
        fields = ('id',  'name', 'name_uz', 'name_ru', 'name_en', 'organization')
        extra_kwargs = {
            'organization': {"required": True},
            'name_uz': {"required": True},
            'name_en': {"required": True},
            'name_ru': {"required": True},
        }


class DepartmentListSerializer(LocaleSerializer):
    organization_detail = OrganizationListPublicSerializer(source="organization", read_only=True)

    class Meta:
        model = Department
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en', 'organization', 'organization_detail')


class DepartmentListPublicSerializer(LocaleSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class PositionSerializer(LocaleSerializer):
    class Meta:
        model = Position
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en', 'department')
        extra_kwargs = {
            'department': {"required": True},
            'name_uz': {"required": True},
            'name_en': {"required": True},
            'name_ru': {"required": True},
        }


class PositionListSerializer(LocaleSerializer):
    department_detail = DepartmentListPublicSerializer(source="department", read_only=True)

    class Meta:
        model = Position
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en', 'department', 'department_detail')


class PositionListPublicSerializer(LocaleSerializer):
    class Meta:
        model = Position
        fields = ('id', 'name')
