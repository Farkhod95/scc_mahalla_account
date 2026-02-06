from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework.generics import ListAPIView

from restapp.filterset import ModelAuditFilter
from restapp.models import ModelAudit
from restapp.pagination import ResultsSetPagination
from restapp.serializers import ModelAuditSerializer


class UserLogsView(ListAPIView):
    serializer_class = ModelAuditSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ModelAuditFilter
    search_fields = ('user__username', 'field_name', 'old_value', 'new_value')
    ordering = ['-id']

    def get_queryset(self):
        return ModelAudit.objects.all()
