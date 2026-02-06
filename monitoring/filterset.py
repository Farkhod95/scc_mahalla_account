import django_filters
from .models import Employee, MahallaInformation, ObjectCategory, Object, CrimeCategory, MahallaCrime, PatrolCar, \
    CameraInformation


class EmployeeFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')

    class Meta:
        model = Employee
        fields = ('organization', 'department', 'position', 'region', 'district', 'mahalla', 'gender', 'full_name', 'phone_number')


class MahallaInformationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    count = django_filters.NumberFilter(field_name='count')

    class Meta:
        model = MahallaInformation
        fields = ('name', 'count')


class ObjectCategoryFilter(django_filters.FilterSet):

    class Meta:
        model = ObjectCategory
        fields = {
            'name': ['exact'],
        }



class ObjectFilter(django_filters.FilterSet):
    organization_name = django_filters.CharFilter(field_name='organization_name', lookup_expr='icontains')
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')

    class Meta:
        model = Object
        fields = ('category', 'organization_name', 'full_name', 'phone_number')


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
        fields = ('category', 'date', 'article', 'description')


class PatrolCarFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(field_name='model', lookup_expr='icontains')
    license_plate = django_filters.CharFilter(field_name='license_plate', lookup_expr='icontains')
    gps_number = django_filters.CharFilter(field_name='gps_number', lookup_expr='icontains')

    class Meta:
        model = PatrolCar
        fields = ('model', 'license_plate', 'gps_number')


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