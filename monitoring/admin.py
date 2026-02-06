from django.contrib import admin
from .models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, PatrolCar, \
    CameraInformation


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'organization', 'department', 'position', 'region', 'district', 'mahalla')
    list_select_related = ('organization', 'department', 'position', 'region', 'district', 'mahalla')
    search_fields = ('full_name', 'phone_number')
    list_filter = ('organization', 'department', 'position', 'region', 'district', 'mahalla', 'gender')
    fields = ('full_name', 'date_of_birthday', 'gender', 'phone_number', 'organization', 'department', 'date_of_appointment', 'position', 'region', 'district', 'mahalla', 'address', 'avatar')


@admin.register(MahallaInformation)
class MahallaInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    search_fields = ('name',)
    fields = ('name', 'count', 'icon')


@admin.register(ObjectCategory)
class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ru', 'name_uz')
    fields = ('name', 'name_en', 'name_ru', 'name_uz')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'full_name', 'phone_number', 'category', 'coordinate_x', 'coordinate_y')
    list_select_related = ('category',)
    search_fields = ('organization_name', 'full_name', 'phone_number')
    list_filter = ('category',)
    fields = ('category', 'organization_name', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


@admin.register(CrimeCategory)
class CrimeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ru', 'name_uz')
    fields = ('name', 'name_en', 'name_ru', 'name_uz')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(MahallaCrime)
class MahallaCrimeAdmin(admin.ModelAdmin):
    list_display = ('article', 'date', 'category', 'coordinate_x', 'coordinate_y')
    list_select_related = ('category',)
    search_fields = ('article', 'description')
    list_filter = ('category', 'date')
    fields = ('category', 'date', 'article', 'description', 'coordinate_x', 'coordinate_y')


@admin.register(PatrolCar)
class PatrolCarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'model', 'gps_number')
    search_fields = ('license_plate', 'model', 'gps_number')
    fields = ('model', 'license_plate', 'gps_number')


@admin.register(CameraInformation)
class CameraInformationAdmin(admin.ModelAdmin):
    list_display = ('status', 'ip_address', 'region', 'district', 'mahalla', 'coordinate_x', 'coordinate_y')
    list_select_related = ('region', 'district', 'mahalla')
    list_filter = ('status', 'region', 'district')
    search_fields = ('ip_address', 'address')
    fields = ('status', 'ip_address', 'region', 'district', 'mahalla', 'address', 'coordinate_x', 'coordinate_y')
