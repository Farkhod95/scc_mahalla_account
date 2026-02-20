import django_filters
from .models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, PatrolCar, \
    CameraInformation, MahallaInformationCategory, OfficeCamera


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