# views.py
from django.db.models import Count, Q
from rest_framework.generics import ListAPIView

from monitoring.models import ObjectCategory
from monitoring.serializers import ObjectCategoryForDashboardSerializer


class ObjectCategoryForDashboardView(ListAPIView):
    serializer_class = ObjectCategoryForDashboardSerializer
    pagination_class = None

    def get_queryset(self):
        mahalla_id = self.request.query_params.get("mahalla_id")

        qs = ObjectCategory.objects.all().order_by("id")

        # mahalla_id bo'lmasa: hammasi bo'yicha count
        if not mahalla_id:
            return qs.annotate(objects_count=Count("category_objects", distinct=True))

        # mahalla_id bo'lsa: mahalla bo'yicha filterlangan count
        # !!! Eslatma: bu yerda yo'l sizda shunaqa deb hisoblayapmiz:
        # Object -> organization -> mahalla
        # Agar sizda boshqacha bo'lsa, shu Q(...) ichidagi yo'lni moslang.
        return qs.annotate(
            objects_count=Count(
                "category_objects",
                filter=Q(category_objects__organization__mahalla_id=mahalla_id),
                distinct=True,
            )
        )
