from monitoring.models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, \
    PatrolCar, CameraInformation, MahallaInformationCategory, OfficeCamera
from rest_framework import serializers

from directory.serializers import RegionListSerializer, DistrictSerializer, OrganizationListPublicSerializer, \
    DepartmentListPublicSerializer, PositionListPublicSerializer, DistrictListSerializer, MahallaListSerializer


class LocaleSerializer(serializers.ModelSerializer):
    name_uz = serializers.CharField(allow_blank=False)
    name_ru = serializers.CharField(allow_blank=False)
    name_en = serializers.CharField(allow_blank=False)



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'date_of_birthday', 'gender', 'phone_number', 'organization', 'department', 'date_of_appointment', 'position', 'region', 'district', 'mahalla', 'address', 'avatar')
        extra_kwargs = {
            'full_name': {"required": True},
            'phone_number': {"required": True},
        }


class EmployeeListSerializer(serializers.ModelSerializer):
    organization_detail = OrganizationListPublicSerializer(source='organization', read_only=True)
    department_detail = DepartmentListPublicSerializer(source='department', read_only=True)
    position_detail = PositionListPublicSerializer(source='position', read_only=True)
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'date_of_birthday', 'gender', 'phone_number', 'organization', 'organization_detail', 'department', 'department_detail', 'date_of_appointment', 'position', 'position_detail', 'region', 'region_detail', 'district', 'district_detail', 'mahalla', 'mahalla_detail', 'address', 'avatar')


class MahallaInformationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MahallaInformationCategory
        fields = ('id', 'name', 'icon')
        extra_kwargs = {
            'name': {"required": False, "allow_blank": True, "allow_null": True},
            'icon': {"required": False, "allow_blank": True, "allow_null": True},
        }


class MahallaInformationCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahallaInformationCategory
        fields = ('id', 'name', 'icon')


class MahallaInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahallaInformation
        fields = ('id', 'count', 'category', 'region', 'district', 'mahalla')
        extra_kwargs = {
            'count': {"required": False},
        }


class MahallaInformationListSerializer(serializers.ModelSerializer):
    category_detail = MahallaInformationCategoryListSerializer(source='category', read_only=True)
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = MahallaInformation
        fields = ('id', 'count', 'category', 'category_detail', 'region', 'region_detail', 'district', 'district_detail', 'mahalla', 'mahalla_detail')


class ObjectCategorySerializer(LocaleSerializer):
    class Meta:
        model = ObjectCategory
        fields = ('id', 'key', 'name', 'name_uz', 'name_ru', 'name_en', 'icon')
        extra_kwargs = {
            'name_uz': {"required": True},
            'name_ru': {"required": True},
            'name_en': {"required": True},
        }


class ObjectCategoryListSerializer(LocaleSerializer):
    class Meta:
        model = ObjectCategory
        fields = ('id', 'key', 'name', 'name_uz', 'name_ru', 'name_en', 'icon')



class ObjectCategoryForDashboardSerializer(serializers.ModelSerializer):
    # Agar siz modeltranslation ishlatayotgan bo'lsangiz, odatda name_uz/name_ru/name_en fieldlari mavjud bo'ladi.
    # Agar sizda boshqa nomlar bo'lsa (masalan name_uz_cyrl, name_kaa), shu yerini moslab qo'ying.
    name_uz = serializers.CharField(read_only=True)
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    icon = serializers.CharField(read_only=True)

    objects_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ObjectCategory
        fields = ("id", 'key', "name_uz", "name_ru", "name_en", 'icon', "objects_count")


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ('id', 'name', 'category', 'organization', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')
        extra_kwargs = {
            'full_name': {"required": True},
            'phone_number': {"required": True},
        }


class ObjectMapSerializer(serializers.ModelSerializer):
    organization_detail = OrganizationListPublicSerializer(source='organization', read_only=True)
    category_detail = ObjectCategoryListSerializer(source='category', read_only=True)

    class Meta:
        model = Object
        fields = ('id', 'name', 'category', 'category_detail','organization', 'organization_detail', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


class ObjectListSerializer(serializers.ModelSerializer):
    category_detail = ObjectCategoryListSerializer(source='category', read_only=True)
    organization_detail = OrganizationListPublicSerializer(source='organization', read_only=True)

    class Meta:
        model = Object
        fields = ('id', 'name', 'category', 'category_detail', 'organization', 'organization_detail', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


class ObjectExcelImportSerializer(serializers.Serializer):
    excel_file = serializers.FileField(
        required=True
    )
    organization_id = serializers.IntegerField(required=True)

    def validate_excel_file(self, value):
        if not value.name.endswith('.xlsx'):
            raise serializers.ValidationError(
                "Faqat .xlsx formatdagi fayllar qabul qilinadi"
            )
        return value


class CrimeCategorySerializer(LocaleSerializer):
    class Meta:
        model = CrimeCategory
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en')
        extra_kwargs = {
            'name_uz': {"required": True},
            'name_ru': {"required": True},
            'name_en': {"required": True},
        }


class CrimeCategoryListSerializer(LocaleSerializer):
    class Meta:
        model = CrimeCategory
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en')


class MahallaCrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahallaCrime
        fields = ('id', 'category', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y', 'region', 'district', 'mahalla')
        extra_kwargs = {
            'article': {"required": True},
        }


class MahallaCrimeMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = MahallaCrime
        fields = ('id', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y')


class MahallaCrimeListSerializer(serializers.ModelSerializer):
    category_detail = ObjectCategoryListSerializer(source='category', read_only=True)
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = MahallaCrime
        fields = ('id', 'category', 'category_detail', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y', 'region', 'region_detail', 'district', 'district_detail', 'mahalla', 'mahalla_detail')


class PatrolCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolCar
        fields = ('id', 'mobjectId', 'mobject_name', 'plate_number', 'imei', 'brand_name', 'group_name', 'last_date', 'coordinate_x', 'coordinate_y')
        # extra_kwargs = {
        #     'mobjectId': {"required": False, "allow_null": True},
        #     'mobject_name': {"required": False, "allow_blank": True, "allow_null": True},
        #     'plate_number': {"required": False, "allow_blank": True, "allow_null": True},
        #     'imei': {"required": False, "allow_blank": True, "allow_null": True},
        #     'brand_name': {"required": False, "allow_blank": True, "allow_null": True},
        #     'group_name': {"required": False, "allow_blank": True, "allow_null": True},
        #     'last_date': {"required": False, "allow_null": True},
        #     'coordinate_x': {"required": False, "allow_blank": True, "allow_null": True},
        #     'coordinate_y': {"required": False, "allow_blank": True, "allow_null": True},
        # }


class PatrolCarGPSSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolCar
        fields = ('id', 'mobjectId', 'mobject_name', 'plate_number', 'imei', 'brand_name', 'group_name', 'last_date', 'coordinate_x', 'coordinate_y')


class PatrolCarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolCar
        fields = ('id', 'mobjectId', 'mobject_name', 'plate_number', 'brand_name', 'group_name', 'last_date')


class CameraInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraInformation
        fields = ('id', 'object_name', 'direction', 'status', 'ip_address', 'region', 'district', 'mahalla', 'address', 'coordinate_x', 'coordinate_y', 'login', 'parol', 'camera_type')
        extra_kwargs = {
            'status': {"required": True},
        }


class CameraInformationMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = CameraInformation
        fields = ('id', 'object_name', 'direction', 'status', 'ip_address', 'address', 'coordinate_x', 'coordinate_y', 'camera_type')


class CameraInformationListSerializer(serializers.ModelSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = CameraInformation
        fields = ('id', 'object_name', 'direction', 'status', 'ip_address', 'region', 'region_detail', 'district', 'district_detail', 'mahalla', 'mahalla_detail', 'address', 'coordinate_x', 'coordinate_y', 'login', 'parol', 'camera_type')


class CameraInformationImportSerializer(serializers.Serializer):
    mahalla_id = serializers.IntegerField(required=True)
    file = serializers.FileField(required=True)

    def validate_file(self, f):
        name = (f.name or "").lower()
        if not (name.endswith(".xlsx") or name.endswith(".xlsm") or name.endswith(".xltx") or name.endswith(".xltm")):
            raise serializers.ValidationError("Fayl formati xlsx bo‘lishi kerak.")
        return f


class OfficeCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeCamera
        fields = ('id', 'object_name', 'direction', 'ip_address', 'region', 'district', 'mahalla', 'address', 'coordinate_x', 'coordinate_y', 'login', 'parol', 'camera_type')


class OfficeCameraListSerializer(serializers.ModelSerializer):
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    mahalla_detail = MahallaListSerializer(source='mahalla', read_only=True)

    class Meta:
        model = OfficeCamera
        fields = ('id', 'object_name', 'direction', 'ip_address', 'region', 'region_detail', 'district', 'district_detail', 'mahalla', 'mahalla_detail', 'address', 'coordinate_x', 'coordinate_y', 'login', 'parol', 'camera_type')