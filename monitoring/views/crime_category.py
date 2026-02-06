from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from monitoring.filterset import CrimeCategoryFilter
from monitoring.models import CrimeCategory
from monitoring.serializers import CrimeCategorySerializer, CrimeCategoryListSerializer


class CrimeCategoryFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in CrimeCategory._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class CrimeCategoryView(ListCreateAPIView):
    serializer_class = CrimeCategoryListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = CrimeCategoryFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['-pk']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CrimeCategory.objects.all()

    def post(self, request, **kwargs):
        serializer = CrimeCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CrimeCategoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CrimeCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CrimeCategory.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        obj = get_object_or_404(CrimeCategory, id=pk)
        serializer = CrimeCategoryListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = get_object_or_404(CrimeCategory, id=pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)
