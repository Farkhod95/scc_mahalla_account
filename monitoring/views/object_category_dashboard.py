# views.py
from rest_framework.generics import ListAPIView
from django.db.models import Count
from monitoring.models import ObjectCategory
from monitoring.serializers import ObjectCategoryForDashboardSerializer


class ObjectCategoryForDashboardView(ListAPIView):
    serializer_class = ObjectCategoryForDashboardSerializer
    pagination_class = None  # dashboard uchun odatda pagination kerak bo'lmaydi

    def get_queryset(self):
        # related_name='category_objects' bo'lgani uchun Count shu nom bilan
        return (
            ObjectCategory.objects
            .annotate(objects_count=Count("category_objects", distinct=True))
            .order_by("id")
        )
