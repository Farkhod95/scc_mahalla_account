import django_filters
from .models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, PatrolCar, \
    CameraInformation, MahallaInformationCategory, OfficeCamera, Shop, ShopCamera, ShopTenant, TenantEmployee, \
    BazarCamera, CenterOfCivilization


class EmployeeFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')

    class Meta:
        model = Employee
        fields = ('organization', 'department', 'position', 'region', 'district', 'mahalla', 'gender', 'full_name', 'phone_number', 'sorting')


class MahallaInformationCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = MahallaInformationCategory
        fields = ('name',)



class MahallaInformationFilter(django_filters.FilterSet):
    count_from = django_filters.NumberFilter(field_name='count', lookup_expr='gte')
    count_to = django_filters.NumberFilter(field_name='count', lookup_expr='lte')

    class Meta:
        model = MahallaInformation
        fields = ('category', 'region', 'district', 'mahalla', 'count')


class ObjectCategoryFilter(django_filters.FilterSet):

    class Meta:
        model = ObjectCategory
        fields = {
            'name': ['exact'],
            'key': ['exact'],
        }



class ObjectFilter(django_filters.FilterSet):
    organization_name = django_filters.CharFilter(field_name='organization__name', lookup_expr='icontains')
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')

    region = django_filters.NumberFilter(field_name='organization__region_id')
    district = django_filters.NumberFilter(field_name='organization__district_id')
    mahalla = django_filters.NumberFilter(field_name='organization__mahalla_id')

    class Meta:
        model = Object
        fields = ('name', 'category', 'organization', 'organization_name', 'full_name', 'phone_number', 'region', 'district', 'mahalla')


class CrimeCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = CrimeCategory
        fields = ('name_uz', 'name_ru', 'name_en')


class MahallaCrimeFilter(django_filters.FilterSet):
    article = django_filters.CharFilter(field_name='article', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = MahallaCrime
        fields = ('category', 'date', 'article', 'description', 'region', 'district', 'mahalla')


class PatrolCarFilter(django_filters.FilterSet):
    mobjectId = django_filters.NumberFilter(field_name='mobjectId')
    mobject_name = django_filters.CharFilter(field_name='mobject_name', lookup_expr='icontains')
    plate_number = django_filters.CharFilter(field_name='plate_number', lookup_expr='icontains')
    imei = django_filters.CharFilter(field_name='imei', lookup_expr='icontains')
    brand_name = django_filters.CharFilter(field_name='brand_name', lookup_expr='icontains')
    group_name = django_filters.CharFilter(field_name='group_name', lookup_expr='icontains')

    last_date = django_filters.DateFilter(field_name='last_date')  # exact
    last_date_from = django_filters.DateFilter(field_name='last_date', lookup_expr='gte')
    last_date_to = django_filters.DateFilter(field_name='last_date', lookup_expr='lte')

    class Meta:
        model = PatrolCar
        fields = ('mobjectId', 'mobject_name', 'plate_number', 'imei', 'brand_name', 'group_name', 'last_date')


class CameraInformationFilter(django_filters.FilterSet):
    object_name = django_filters.CharFilter(field_name='object_name', lookup_expr='icontains')
    direction = django_filters.CharFilter(field_name='direction', lookup_expr='icontains')
    ip_address = django_filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    address = django_filters.CharFilter(field_name='address', lookup_expr='icontains')
    login = django_filters.CharFilter(field_name='login', lookup_expr='icontains')
    camera_type = django_filters.CharFilter(field_name='camera_type', lookup_expr='icontains')

    class Meta:
        model = CameraInformation
        fields = ('status', 'camera_type', 'region', 'district', 'mahalla', 'object_name', 'direction', 'ip_address', 'address', 'login')


class OfficeCameraFilter(django_filters.FilterSet):
    object_name = django_filters.CharFilter(field_name='object_name', lookup_expr='icontains')
    direction = django_filters.CharFilter(field_name='direction', lookup_expr='icontains')
    ip_address = django_filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    address = django_filters.CharFilter(field_name='address', lookup_expr='icontains')
    login = django_filters.CharFilter(field_name='login', lookup_expr='icontains')
    camera_type = django_filters.CharFilter(field_name='camera_type', lookup_expr='icontains')

    class Meta:
        model = OfficeCamera
        fields = ('region', 'district', 'mahalla', 'camera_type', 'object_name', 'direction', 'ip_address', 'address', 'login')


class ShopFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
    owner_company_name = django_filters.CharFilter(field_name='owner_company_name', lookup_expr='icontains')
    owner_fio = django_filters.CharFilter(field_name='owner_fio', lookup_expr='icontains')
    owner_jshshir = django_filters.CharFilter(field_name='owner_jshshir', lookup_expr='icontains')
    owner_phone = django_filters.CharFilter(field_name='owner_phone', lookup_expr='icontains')
    total_area_from = django_filters.NumberFilter(field_name='total_area', lookup_expr='gte')
    total_area_to = django_filters.NumberFilter(field_name='total_area', lookup_expr='lte')
    tenants_count_from = django_filters.NumberFilter(field_name='tenants_count', lookup_expr='gte')
    tenants_count_to = django_filters.NumberFilter(field_name='tenants_count', lookup_expr='lte')

    class Meta:
        model = Shop
        fields = ('block_type', 'shop_number', 'code', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone', 'tenants_count', 'total_area', 'code')


class ShopCameraFilter(django_filters.FilterSet):
    url = django_filters.CharFilter(field_name='url', lookup_expr='icontains')

    class Meta:
        model = ShopCamera
        fields = ('shop', 'url')


import django_filters

from monitoring.models import ShopTenant


class ShopTenantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    leader_fio = django_filters.CharFilter(field_name='leader_fio', lookup_expr='icontains')
    leader_jshshir = django_filters.CharFilter(field_name='leader_jshshir', lookup_expr='icontains')
    leader_phone = django_filters.CharFilter(field_name='leader_phone', lookup_expr='icontains')
    stir = django_filters.CharFilter(field_name='stir', lookup_expr='icontains')
    certificate_number = django_filters.CharFilter(field_name='certificate_number', lookup_expr='icontains')
    cash_register_number = django_filters.CharFilter(field_name='cash_register_number', lookup_expr='icontains')
    rented_area_from = django_filters.NumberFilter(field_name='rented_area', lookup_expr='gte')
    rented_area_to = django_filters.NumberFilter(field_name='rented_area', lookup_expr='lte')
    employees_count_from = django_filters.NumberFilter(field_name='employees_count', lookup_expr='gte')
    employees_count_to = django_filters.NumberFilter(field_name='employees_count', lookup_expr='lte')
    monthly_checks_count_from = django_filters.NumberFilter(field_name='monthly_checks_count', lookup_expr='gte')
    monthly_checks_count_to = django_filters.NumberFilter(field_name='monthly_checks_count', lookup_expr='lte')
    daily_checks_count_from = django_filters.NumberFilter(field_name='daily_checks_count', lookup_expr='gte')
    daily_checks_count_to = django_filters.NumberFilter(field_name='daily_checks_count', lookup_expr='lte')
    monthly_visitors_from = django_filters.NumberFilter(field_name='monthly_visitors', lookup_expr='gte')
    monthly_visitors_to = django_filters.NumberFilter(field_name='monthly_visitors', lookup_expr='lte')
    daily_visitors_from = django_filters.NumberFilter(field_name='daily_visitors', lookup_expr='gte')
    daily_visitors_to = django_filters.NumberFilter(field_name='daily_visitors', lookup_expr='lte')
    ytd_okkm_from = django_filters.NumberFilter(field_name='ytd_okkm', lookup_expr='gte')
    ytd_okkm_to = django_filters.NumberFilter(field_name='ytd_okkm', lookup_expr='lte')
    ytd_e_invoice_from = django_filters.NumberFilter(field_name='ytd_e_invoice', lookup_expr='gte')
    ytd_e_invoice_to = django_filters.NumberFilter(field_name='ytd_e_invoice', lookup_expr='lte')
    ytd_qr_from = django_filters.NumberFilter(field_name='ytd_qr', lookup_expr='gte')
    ytd_qr_to = django_filters.NumberFilter(field_name='ytd_qr', lookup_expr='lte')
    mtd_okkm_from = django_filters.NumberFilter(field_name='mtd_okkm', lookup_expr='gte')
    mtd_okkm_to = django_filters.NumberFilter(field_name='mtd_okkm', lookup_expr='lte')
    mtd_e_invoice_from = django_filters.NumberFilter(field_name='mtd_e_invoice', lookup_expr='gte')
    mtd_e_invoice_to = django_filters.NumberFilter(field_name='mtd_e_invoice', lookup_expr='lte')
    mtd_qr_from = django_filters.NumberFilter(field_name='mtd_qr', lookup_expr='gte')
    mtd_qr_to = django_filters.NumberFilter(field_name='mtd_qr', lookup_expr='lte')
    dtd_okkm_from = django_filters.NumberFilter(field_name='dtd_okkm', lookup_expr='gte')
    dtd_okkm_to = django_filters.NumberFilter(field_name='dtd_okkm', lookup_expr='lte')
    dtd_e_invoice_from = django_filters.NumberFilter(field_name='dtd_e_invoice', lookup_expr='gte')
    dtd_e_invoice_to = django_filters.NumberFilter(field_name='dtd_e_invoice', lookup_expr='lte')
    dtd_qr_from = django_filters.NumberFilter(field_name='dtd_qr', lookup_expr='gte')
    dtd_qr_to = django_filters.NumberFilter(field_name='dtd_qr', lookup_expr='lte')

    class Meta:
        model = ShopTenant
        fields = ('shop', 'business_type', 'tax_type', 'activity_status', 'fire_safety_level', 'has_fire_alarm',
                  'is_red_category', 'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'stir', 'certificate_number',
                  'cash_register_number', 'employees_count', 'monthly_checks_count', 'daily_checks_count',
                  'monthly_visitors', 'daily_visitors')


class TenantEmployeeFilter(django_filters.FilterSet):
    fio = django_filters.CharFilter(field_name='fio', lookup_expr='icontains')
    jshshir = django_filters.CharFilter(field_name='jshshir', lookup_expr='icontains')
    phone = django_filters.CharFilter(field_name='phone', lookup_expr='icontains')

    class Meta:
        model = TenantEmployee
        fields = ('tenant', 'fio', 'jshshir', 'phone')


class BazarCameraFilter(django_filters.FilterSet):
    object_name = django_filters.CharFilter(field_name='object_name', lookup_expr='icontains')
    url = django_filters.CharFilter(field_name='url', lookup_expr='icontains')
    login = django_filters.CharFilter(field_name='login', lookup_expr='icontains')

    class Meta:
        model = BazarCamera
        fields = ('type', 'camera_type', 'location_type', 'ip_address', 'region', 'district', 'mahalla', 'object_name', 'url', 'login', 'is_active')


class CenterOfCivilizationFilter(django_filters.FilterSet):
    object_name = django_filters.CharFilter(field_name='object_name', lookup_expr='icontains')
    url = django_filters.CharFilter(field_name='url', lookup_expr='icontains')
    login = django_filters.CharFilter(field_name='login', lookup_expr='icontains')

    class Meta:
        model = CenterOfCivilization
        fields = ('type', 'camera_type', 'ip_address', 'region', 'district', 'mahalla', 'object_name', 'url', 'login', 'is_active')