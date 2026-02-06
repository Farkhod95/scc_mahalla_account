from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.services.excel_import import import_objects_from_excel
from restapp.pagination import ResultsSetPagination
from monitoring.filterset import ObjectFilter
from monitoring.models import Object
from monitoring.serializers import ObjectSerializer, ObjectListSerializer, ObjectMapSerializer, \
    ObjectExcelImportSerializer


class ObjectFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in Object._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class ObjectForMapView(ListCreateAPIView):
    serializer_class = ObjectMapSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ObjectFilter
    search_fields = ('organization__name', 'full_name', 'phone_number')
    ordering = ['-pk']
    http_method_names = ['get']

    def get_queryset(self):
        return Object.objects.select_related('category', 'organization').all()


class ObjectView(ListCreateAPIView):
    serializer_class = ObjectListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ObjectFilter
    search_fields = ('organization__name', 'full_name', 'phone_number')
    ordering = ['-pk']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Object.objects.select_related('category', 'organization').all()

    def post(self, request, **kwargs):
        serializer = ObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ObjectDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ObjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Object.objects.select_related('category', 'organization').all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        obj = get_object_or_404(Object, id=pk)
        serializer = ObjectListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = get_object_or_404(Object, id=pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)


class ObjectExcelImportView(CreateAPIView):
    serializer_class = ObjectExcelImportSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ObjectExcelImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        excel_file = serializer.validated_data['excel_file']
        organization_id = serializer.validated_data['organization_id']

        result = import_objects_from_excel(
            excel_file=excel_file,
            created_by_user=request.user,
            organization_id=organization_id
        )

        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
