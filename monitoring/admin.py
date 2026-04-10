from django.contrib import admin

from directory.models import Region, District, Gom, Mahalla
from .models import (
    Employee,
    MahallaInformation,
    ObjectCategory,
    Object,
    CrimeCategory,
    MahallaCrime,
    PatrolCar,
    CameraInformation,
    MahallaInformationCategory,
    OfficeCamera,
    ShopCamera,
    Shop,
    ShopTenant,
    TenantEmployee,
    BazarCamera,
    CenterOfCivilization,
    MFYCitizen,
)


class ActiveLocationForeignKeyMixin:
    """
    Region/District/Gom/Mahalla selectlarida faqat is_active=True bo'lgan yozuvlarni chiqaradi.
    """

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            kwargs["queryset"] = Region.objects.filter(is_active=True)
        elif db_field.name == "district":
            kwargs["queryset"] = District.objects.filter(is_active=True)
        elif db_field.name == "gom":
            kwargs["queryset"] = Gom.objects.filter(is_active=True)
        elif db_field.name == "mahalla":
            kwargs["queryset"] = Mahalla.objects.filter(is_active=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Employee)
class EmployeeAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'sorting', 'full_name', 'phone_number', 'organization',
        'department', 'position', 'region', 'district', 'gom', 'mahalla'
    )
    list_select_related = (
        'organization', 'department', 'position',
        'region', 'district', 'gom', 'mahalla'
    )
    search_fields = ('full_name', 'phone_number')
    list_filter = (
        'organization', 'department', 'position',
        'region', 'district', 'gom', 'mahalla', 'gender'
    )
    fields = (
        'sorting', 'full_name', 'date_of_birthday', 'gender', 'phone_number',
        'organization', 'department', 'date_of_appointment', 'position',
        'region', 'district', 'gom', 'mahalla', 'address', 'avatar'
    )


@admin.register(MahallaInformationCategory)
class MahallaInformationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fields = ('name', 'icon')


@admin.register(MahallaInformation)
class MahallaInformationAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = ('region', 'district', 'gom', 'mahalla', 'count', 'category')
    list_select_related = ('category', 'region', 'district', 'gom', 'mahalla')
    list_filter = ('category', 'region', 'district', 'gom', 'mahalla')
    search_fields = ('count',)
    fields = ('region', 'district', 'gom', 'mahalla', 'count', 'category')


@admin.register(ObjectCategory)
class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('key', 'name_en', 'name_ru', 'name_uz', 'color', 'icon_color')
    fields = ('key', 'name', 'name_en', 'name_ru', 'name_uz', 'icon', 'color', 'icon_color')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(Object)
class ObjectAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'name', 'category', 'organization', 'full_name', 'phone_number',
        'region', 'district', 'gom', 'mahalla',
        'coordinate_x', 'coordinate_y', 'avatar'
    )
    list_select_related = (
        'category', 'organization', 'region', 'district', 'gom', 'mahalla'
    )
    search_fields = ('name', 'organization__name', 'full_name', 'phone_number')
    list_filter = ('category', 'organization', 'region', 'district', 'gom', 'mahalla')
    fields = (
        'name', 'category', 'organization', 'full_name', 'avatar',
        'phone_number', 'address', 'coordinate_x', 'coordinate_y',
        'region', 'district', 'gom', 'mahalla'
    )


@admin.register(CrimeCategory)
class CrimeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ru', 'name_uz')
    fields = ('name', 'name_en', 'name_ru', 'name_uz')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(MahallaCrime)
class MahallaCrimeAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'region', 'district', 'gom', 'mahalla',
        'article', 'date', 'category', 'coordinate_x', 'coordinate_y'
    )
    list_select_related = ('category', 'region', 'district', 'gom', 'mahalla')
    search_fields = ('article', 'description')
    list_filter = ('category', 'date', 'region', 'district', 'gom', 'mahalla')
    fields = (
        'region', 'district', 'gom', 'mahalla',
        'category', 'date', 'article', 'description',
        'coordinate_x', 'coordinate_y'
    )


@admin.register(PatrolCar)
class PatrolCarAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'brand_name', 'mobject_name', 'imei', 'mobjectId', 'group_name', 'last_date')
    search_fields = ('plate_number', 'brand_name', 'mobject_name', 'imei', 'group_name', 'mobjectId')
    list_filter = ('brand_name', 'group_name', 'last_date')
    fields = ('mobjectId', 'mobject_name', 'plate_number', 'imei', 'brand_name', 'group_name', 'last_date', 'coordinate_x', 'coordinate_y')


@admin.register(CameraInformation)
class CameraInformationAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'object_name', 'direction', 'status', 'ip_address', 'camera_type',
        'region', 'district', 'gom', 'mahalla', 'coordinate_x', 'coordinate_y'
    )
    list_select_related = ('region', 'district', 'gom', 'mahalla')
    list_filter = ('status', 'camera_type', 'region', 'district', 'gom', 'mahalla')
    search_fields = ('object_name', 'direction', 'ip_address', 'address', 'login', 'camera_type')
    fields = (
        'object_name', 'direction', 'status', 'ip_address',
        'login', 'parol', 'camera_type',
        'region', 'district', 'gom', 'mahalla',
        'address', 'coordinate_x', 'coordinate_y'
    )


@admin.register(OfficeCamera)
class OfficeCameraAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'object_name', 'direction', 'ip_address', 'camera_type',
        'region', 'district', 'gom', 'mahalla',
        'coordinate_x', 'coordinate_y', 'camera_url'
    )
    list_select_related = ('region', 'district', 'gom', 'mahalla')
    list_filter = ('camera_type', 'region', 'district', 'gom', 'mahalla')
    search_fields = ('object_name', 'direction', 'ip_address', 'address', 'login', 'camera_type')
    fields = (
        'object_name', 'direction', 'ip_address',
        'login', 'parol', 'camera_type',
        'region', 'district', 'gom', 'mahalla',
        'address', 'coordinate_x', 'coordinate_y', 'camera_url'
    )


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('block_type', 'shop_number', 'code', 'owner_company_name', 'owner_fio', 'owner_phone', 'total_area', 'tenants_count')
    list_filter = ('block_type',)
    search_fields = ('shop_number', 'code', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone')
    ordering = ('block_type', 'shop_number')
    fields = ('block_type', 'shop_number', 'code', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone', 'avatar', 'total_area', 'tenants_count')


@admin.register(ShopCamera)
class ShopCameraAdmin(admin.ModelAdmin):
    list_display = ('shop', 'title', 'url')
    list_select_related = ('shop',)
    list_filter = ('shop',)
    search_fields = ('url', 'shop__owner_fio')
    fields = ('shop', 'title', 'url')


@admin.register(ShopTenant)
class ShopTenantAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'shop', 'name', 'business_type', 'tax_type', 'activity_status',
        'leader_fio', 'leader_phone', 'stir', 'certificate_number',
        'employees_count', 'rented_area', 'is_red_category'
    )
    list_filter = ('business_type', 'tax_type', 'activity_status', 'fire_safety_level', 'has_fire_alarm', 'is_red_category')
    search_fields = ('name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'stir', 'certificate_number', 'cash_register_number')
    ordering = ('-id',)
    fields = (
        'shop', 'rented_area', 'business_type', 'tax_type', 'activity_status',
        'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'avatar',
        'stir', 'certificate_number', 'employees_count', 'cash_register_number',
        'ytd_okkm', 'ytd_e_invoice', 'ytd_qr',
        'mtd_okkm', 'mtd_e_invoice', 'mtd_qr',
        'dtd_okkm', 'dtd_e_invoice', 'dtd_qr',
        'monthly_checks_count', 'daily_checks_count',
        'monthly_visitors', 'daily_visitors',
        'fire_safety_level', 'has_fire_alarm', 'extinguisher_info',
        'is_red_category', 'red_reason'
    )


@admin.register(TenantEmployee)
class TenantEmployeeAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'fio', 'jshshir', 'phone')
    list_select_related = ('tenant',)
    list_filter = ('tenant',)
    search_fields = ('fio', 'jshshir', 'phone', 'tenant__name', 'tenant__stir', 'tenant__certificate_number')
    fields = ('tenant', 'fio', 'jshshir', 'phone', 'avatar')


@admin.register(BazarCamera)
class BazarCameraAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'object_name', 'ip_address', 'type', 'location_type', 'camera_type',
        'url', 'coordinate_x', 'coordinate_y',
        'region', 'district', 'mahalla', 'is_active'
    )
    list_filter = ('type', 'camera_type', 'location_type', 'region', 'district', 'mahalla', 'is_active')
    search_fields = ('object_name', 'ip_address', 'url', 'login')
    fields = (
        'object_name', 'ip_address', 'type', 'location_type', 'camera_type',
        'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol',
        'region', 'district', 'mahalla', 'is_active'
    )


@admin.register(CenterOfCivilization)
class CenterOfCivilizationAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        'object_name', 'ip_address', 'type', 'camera_type',
        'url', 'coordinate_x', 'coordinate_y',
        'region', 'district', 'mahalla', 'is_active'
    )
    list_filter = ('type', 'camera_type', 'region', 'district', 'mahalla', 'is_active')
    search_fields = ('object_name', 'ip_address', 'url', 'login')
    fields = (
        'object_name', 'ip_address', 'type', 'camera_type',
        'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol',
        'region', 'district', 'mahalla', 'is_active'
    )


@admin.register(MFYCitizen)
class MFYCitizenAdmin(ActiveLocationForeignKeyMixin, admin.ModelAdmin):
    list_display = ('full_name', 'category', 'avatar', 'region', 'district', 'mahalla', 'is_active')
    list_filter = ('category', 'region', 'district', 'mahalla', 'is_active')
    search_fields = ('full_name', 'address', 'phone')
    fields = (
        'full_name', 'category', 'address', 'avatar', 'phone',
        'degree', 'type', 'coordinate_x', 'coordinate_y',
        'region', 'district', 'mahalla',
        'is_active'
    )