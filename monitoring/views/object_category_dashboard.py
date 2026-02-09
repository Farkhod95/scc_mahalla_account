# views.py
from django.db.models import Count, Q
from django.db.models.functions import Coalesce
from django.db.models import IntegerField
from django.db.models import FilteredRelation

from rest_framework.generics import ListAPIView

from monitoring.models import ObjectCategory
from monitoring.serializers import ObjectCategoryForDashboardSerializer


class ObjectCategoryForDashboardView(ListAPIView):
    serializer_class = ObjectCategoryForDashboardSerializer
    pagination_class = None

    def get_queryset(self):
        mahalla_id = self.request.query_params.get("mahalla_id")

        qs = ObjectCategory.objects.all()

        # mahalla_id kelmasa: eski logika (hammasi bo‘yicha count)
        if not mahalla_id:
            return (
                qs.annotate(objects_count=Count("category_objects", distinct=True))
                  .order_by("id")
            )

        # mahalla_id bo‘lsa: Object larni organization__mahalla_id bo‘yicha filterlab count
        # Eslatma: Agar sizda yo‘l boshqacha bo‘lsa, shu joyni moslang:
        # masalan: category_objects__mahalla_id yoki organization__district_id va h.k.
        return (
            qs.annotate(
                filtered_objects=FilteredRelation(
                    "category_objects",
                    condition=Q(category_objects__organization__mahalla_id=mahalla_id)
                )
            )
            .annotate(
                objects_count=Coalesce(
                    Count("filtered_objects", distinct=True),
                    0,
                    output_field=IntegerField()
                )
            )
            .order_by("id")
        )
