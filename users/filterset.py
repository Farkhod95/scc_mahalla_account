from django_filters.rest_framework import FilterSet

from users.models import User


class UserFilter(FilterSet):

    class Meta:
        model = User
        fields = {
            'username': ['exact', 'startswith', 'contains'],
            'last_name': ['exact'],
            'first_name': ['exact'],
            'second_name': ['exact'],
            'is_active': ['exact'],
            'organization': ['exact'],
            'department': ['exact'],
            'position': ['exact'],
            'region': ['exact'],
            'district': ['exact'],
            'pinfl': ['exact'],
            'gender': ['exact'],
            'role': ['exact'],
        }