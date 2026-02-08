from django_filters.rest_framework import FilterSet

from directory.models import District, Region, Mahalla, Organization, Position, Department


class DistrictFilter(FilterSet):

    class Meta:
        model = District
        fields = {
            'code': ['exact'],
            'region': ['exact'],
        }


class RegionssFilter(FilterSet):

    class Meta:
        model = Region
        fields = {
            'name': ['exact'],
            'code': ['exact'],
        }


class MahallaFilter(FilterSet):

    class Meta:
        model = Mahalla
        fields = {
            'code': ['exact'],
            'region': ['exact'],
            'district': ['exact'],
        }


class OrganizationFilter(FilterSet):

    class Meta:
        model = Organization
        fields = {
            'number': ['exact'],
            'code': ['exact'],
            'region': ['exact'],
            'district': ['exact'],
            'mahalla': ['exact'],
        }


class PositionFilter(FilterSet):

    class Meta:
        model = Position
        fields = {
            'name': ['exact'],
            'department': ['exact'],
        }


class DepartmentFilter(FilterSet):

    class Meta:
        model = Department
        fields = {
            'name': ['exact'],
        }
