from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.filterset import DepartmentFilter
from directory.models import Department
from directory.serializers import DepartmentSerializer, DepartmentListSerializer

from restapp.pagination import ResultsSetPagination
from rest_framework.permissions import AllowAny


class DepartmentFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []

        for field in Department._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class DepartmentView(ListCreateAPIView):
    serializer_class = DepartmentListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DepartmentFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['-pk']

    def get_queryset(self):
        return Department.objects.all()

    def post(self, request, **kwargs):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class DepartmentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        region = get_object_or_404(Department, id=pk)
        serializer = DepartmentListSerializer(region)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        department = get_object_or_404(Department, id=pk)
        serializer = self.serializer_class(department, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)
