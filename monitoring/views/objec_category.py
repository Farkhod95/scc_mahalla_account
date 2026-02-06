from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from monitoring.filterset import ObjectCategoryFilter
from monitoring.models import ObjectCategory
from monitoring.serializers import ObjectCategorySerializer, ObjectCategoryListSerializer


class ObjectCategoryFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in ObjectCategory._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class ObjectCategoryView(ListCreateAPIView):
    serializer_class = ObjectCategoryListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ObjectCategoryFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['-pk']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ObjectCategory.objects.all()

    def post(self, request, **kwargs):
        serializer = ObjectCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ObjectCategoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ObjectCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ObjectCategory.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        obj = get_object_or_404(ObjectCategory, id=pk)
        serializer = ObjectCategoryListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = get_object_or_404(ObjectCategory, id=pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)
