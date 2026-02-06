from monitoring.models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, \
    PatrolCar, CameraInformation
from rest_framework import serializers

from directory.serializers import RegionListSerializer, DistrictSerializer, OrganizationListPublicSerializer, \
    DepartmentListPublicSerializer, PositionListPublicSerializer, DistrictListSerializer, MahallaListSerializer
import requests
from datetime import datetime
from users.serializers import UserListPublicSerializer
from django.conf import settings
from rest_framework.exceptions import ValidationError
from users.models import User


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


class MahallaInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahallaInformation
        fields = ('id', 'name', 'count', 'icon')
        extra_kwargs = {
            'name': {"required": False, "allow_blank": True, "allow_null": True},
            'count': {"required": False},
            'icon': {"required": False, "allow_blank": True, "allow_null": True},
        }


class MahallaInformationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahallaInformation
        fields = ('id', 'name', 'count', 'icon')


class ObjectCategorySerializer(LocaleSerializer):
    class Meta:
        model = ObjectCategory
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en')
        extra_kwargs = {
            'name_uz': {"required": True},
            'name_ru': {"required": True},
            'name_en': {"required": True},
        }


class ObjectCategoryListSerializer(LocaleSerializer):
    class Meta:
        model = ObjectCategory
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en')


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ('id', 'category', 'organization_name', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')
        extra_kwargs = {
            'full_name': {"required": True},
            'phone_number': {"required": True},
        }


class ObjectMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = Object
        fields = ('id', 'organization_name', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


class ObjectListSerializer(serializers.ModelSerializer):
    category_detail = ObjectCategoryListSerializer(source='category', read_only=True)

    class Meta:
        model = Object
        fields = ('id', 'category', 'category_detail', 'organization_name', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


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
        fields = ('id', 'category', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y')
        extra_kwargs = {
            'article': {"required": True},
        }


class MahallaCrimeMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = MahallaCrime
        fields = ('id', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y')


class MahallaCrimeListSerializer(serializers.ModelSerializer):
    category_detail = ObjectCategoryListSerializer(source='category', read_only=True)

    class Meta:
        model = MahallaCrime
        fields = ('id', 'category', 'category_detail', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y')


class PatrolCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolCar
        fields = ('id', 'model', 'license_plate', 'gps_number')
        extra_kwargs = {
            'model': {"required": False, "allow_blank": True, "allow_null": True},
            'license_plate': {"required": False, "allow_blank": True, "allow_null": True},
            'gps_number': {"required": False, "allow_blank": True, "allow_null": True},
        }


class PatrolCarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolCar
        fields = ('id', 'model', 'license_plate', 'gps_number')


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