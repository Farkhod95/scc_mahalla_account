from django.contrib import admin
from .models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, PatrolCar, \
    CameraInformation, MahallaInformationCategory, OfficeCamera, ShopCamera, Shop, ShopTenant, TenantEmployee, \
    BazarCamera, CenterOfCivilization, MFYCitizen


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('sorting', 'full_name', 'phone_number', 'organization', 'department', 'position', 'region', 'district', 'mahalla')
    list_select_related = ('organization', 'department', 'position', 'region', 'district', 'mahalla')
    search_fields = ('full_name', 'phone_number')
    list_filter = ('organization', 'department', 'position', 'region', 'district', 'mahalla', 'gender')
    fields = ('sorting', 'full_name', 'date_of_birthday', 'gender', 'phone_number', 'organization', 'department', 'date_of_appointment', 'position', 'region', 'district', 'mahalla', 'address', 'avatar')


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
    list_display = ('key','name_en', 'name_ru', 'name_uz', 'color', 'icon_color')
    fields = ('key', 'name', 'name_en', 'name_ru', 'name_uz', 'icon' , 'color', 'icon_color')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'organization', 'full_name', 'phone_number', 'category', 'coordinate_x', 'coordinate_y', 'avatar')
    list_select_related = ('category', 'organization')
    search_fields = ('name', 'organization__name', 'full_name', 'phone_number')
    list_filter = ('category', 'organization')
    fields = ('name', 'category', 'organization', 'full_name', 'avatar', 'phone_number', 'address', 'coordinate_x', 'coordinate_y')


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
    list_display = ('object_name', 'direction', 'ip_address', 'camera_type', 'region', 'district', 'mahalla', 'coordinate_x', 'coordinate_y', 'camera_url')
    list_select_related = ('region', 'district', 'mahalla')
    list_filter = ('camera_type', 'region', 'district', 'mahalla')
    search_fields = ('object_name', 'direction', 'ip_address', 'address', 'login', 'camera_type')
    fields = ('object_name', 'direction', 'ip_address', 'login', 'parol', 'camera_type', 'region', 'district', 'mahalla', 'address', 'coordinate_x', 'coordinate_y', 'camera_url')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('block_type', 'shop_number', 'code',  'owner_company_name', 'owner_fio', 'owner_phone', 'total_area', 'tenants_count')
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
    list_display = ('id', 'shop', 'name', 'business_type', 'tax_type', 'activity_status', 'leader_fio', 'leader_phone', 'stir', 'certificate_number', 'employees_count', 'rented_area', 'is_red_category')
    list_filter = ('business_type', 'tax_type', 'activity_status', 'fire_safety_level', 'has_fire_alarm', 'is_red_category')
    search_fields = ('name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'stir', 'certificate_number', 'cash_register_number')
    ordering = ('-id',)
    fields = ('shop', 'rented_area', 'business_type', 'tax_type', 'activity_status', 'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'avatar', 'stir', 'certificate_number', 'employees_count', 'cash_register_number', 'ytd_okkm', 'ytd_e_invoice', 'ytd_qr', 'mtd_okkm', 'mtd_e_invoice', 'mtd_qr', 'dtd_okkm', 'dtd_e_invoice', 'dtd_qr', 'monthly_checks_count', 'daily_checks_count', 'monthly_visitors', 'daily_visitors', 'fire_safety_level', 'has_fire_alarm', 'extinguisher_info', 'is_red_category', 'red_reason')


@admin.register(TenantEmployee)
class TenantEmployeeAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'fio', 'jshshir', 'phone')
    list_select_related = ('tenant',)
    list_filter = ('tenant',)
    search_fields = ('fio', 'jshshir', 'phone', 'tenant__name', 'tenant__stir', 'tenant__certificate_number')
    fields = ('tenant', 'fio', 'jshshir', 'phone', 'avatar')


@admin.register(BazarCamera)
class BazarCameraAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'ip_address', 'type', 'location_type', 'camera_type', 'url', 'coordinate_x', 'coordinate_y', 'region', 'district', 'mahalla', 'is_active')
    list_filter = ('type', 'camera_type', 'location_type', 'region', 'district', 'is_active')
    search_fields = ('object_name', 'ip_address', 'url', 'login')
    fields = ('object_name', 'ip_address', 'type', 'location_type', 'camera_type', 'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol', 'region', 'district', 'mahalla', 'is_active')


@admin.register(CenterOfCivilization)
class CenterOfCivilizationAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'ip_address', 'type', 'camera_type', 'url', 'coordinate_x', 'coordinate_y', 'region', 'district', 'mahalla', 'is_active')
    list_filter = ('type', 'camera_type', 'region', 'district', 'is_active')
    search_fields = ('object_name', 'ip_address', 'url', 'login')
    fields = ('object_name', 'ip_address', 'type', 'camera_type', 'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol', 'region', 'district', 'mahalla', 'is_active')


@admin.register(MFYCitizen)
class MFYCitizenAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'category', 'avatar', 'region', 'district', 'mahalla', 'is_active')
    list_filter = ('category', 'region', 'district', 'is_active')
    search_fields = ('full_name', 'avatar', 'address')
    fields = (
        'full_name', 'category', 'address', 'avatar', 'image',
        'degree', 'type', 'location',
        'region', 'district', 'mahalla',
        'is_active'
    )
