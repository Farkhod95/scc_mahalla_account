from django_filters.rest_framework import FilterSet

from restapp.models import ModelAudit


class ModelAuditFilter(FilterSet):

    class Meta:
        model = ModelAudit
        fields = ['module']

    @property
    def qs(self):
        parent = super().qs
        instance_id = getattr(self.request, 'id', None)
        instance = getattr(self.request, 'module', None)
        if instance_id and instance:
            return parent.filter(instance_id=instance_id) & parent.filter(instance=instance)
        else:
            return parent