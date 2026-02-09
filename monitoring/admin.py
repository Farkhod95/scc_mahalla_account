from django.contrib import admin
from .models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, PatrolCar, \
    CameraInformation, MahallaInformationCategory, OfficeCamera


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'organization', 'department', 'position', 'region', 'district', 'mahalla')
    list_select_related = ('organization', 'department', 'position', 'region', 'district', 'mahalla')
    search_fields = ('full_name', 'phone_number')
    list_filter = ('organization', 'department', 'position', 'region', 'district', 'mahalla', 'gender')
    fields = ('full_name', 'date_of_birthday', 'gender', 'phone_number', 'organization', 'department', 'date_of_appointment', 'position', 'region', 'district', 'mahalla', 'address', 'avatar')


@admin.register(MahallaInformationCategory)
class MahallaInformationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fields = ('name', 'icon')


@admin.register(MahallaInformation)
class MahallaInformationAdmin(admin.ModelAdmin):
    list_display = ('region', 'district', 'mahalla', 'count', 'category')
    list_select_related = ('category', 'region', 'district', 'mahalla')
    list_filter = ('category', 'region', 'district', 'mahalla')
    search_fields = ('count',)
    fields = ('region', 'district', 'mahalla', 'count', 'category')


@admin.register(ObjectCategory)
class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('key','name_en', 'name_ru', 'name_uz')
    fields = ('key', 'name', 'name_en', 'name_ru', 'name_uz', 'icon')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('organization', 'full_name', 'phone_number', 'category', 'coordinate_x', 'coordinate_y', 'avatar')
    list_select_related = ('category', 'organization')
    search_fields = ('organization__name', 'full_name', 'phone_number')
    list_filter = ('category', 'organization')
    fields = ('category', 'organization', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


@admin.register(CrimeCategory)
class CrimeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ru', 'name_uz')
    fields = ('name', 'name_en', 'name_ru', 'name_uz')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(MahallaCrime)
class MahallaCrimeAdmin(admin.ModelAdmin):
    list_display = ('region', 'district', 'mahalla', 'article', 'date', 'category', 'coordinate_x', 'coordinate_y')
    list_select_related = ('category',)
    search_fields = ('article', 'description')
    list_filter = ('category', 'date')
    fields = ('region', 'district', 'mahalla', 'category', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y')


@admin.register(PatrolCar)
class PatrolCarAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'brand_name', 'mobject_name', 'imei', 'mobjectId', 'group_name', 'last_date')
    search_fields = ('plate_number', 'brand_name', 'mobject_name', 'imei', 'group_name', 'mobjectId')
    list_filter = ('brand_name', 'group_name', 'last_date')
    fields = ('mobjectId', 'mobject_name', 'plate_number', 'imei', 'brand_name', 'group_name', 'last_date', 'coordinate_x', 'coordinate_y')


@admin.register(CameraInformation)
class CameraInformationAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'direction', 'status', 'ip_address', 'camera_type', 'region', 'district', 'mahalla', 'coordinate_x', 'coordinate_y')
    list_select_related = ('region', 'district', 'mahalla')
    list_filter = ('status', 'camera_type', 'region', 'district', 'mahalla')
    search_fields = ('object_name', 'direction', 'ip_address', 'address', 'login', 'camera_type')
    fields = ('object_name', 'direction', 'status', 'ip_address', 'login', 'parol', 'camera_type', 'region', 'district', 'mahalla', 'address', 'coordinate_x', 'coordinate_y')


@admin.register(OfficeCamera)
class OfficeCameraAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'direction', 'ip_address', 'camera_type', 'region', 'district', 'mahalla', 'coordinate_x', 'coordinate_y')
    list_select_related = ('region', 'district', 'mahalla')
    list_filter = ('camera_type', 'region', 'district', 'mahalla')
    search_fields = ('object_name', 'direction', 'ip_address', 'address', 'login', 'camera_type')
    fields = ('object_name', 'direction', 'ip_address', 'login', 'parol', 'camera_type', 'region', 'district', 'mahalla', 'address', 'coordinate_x', 'coordinate_y')
