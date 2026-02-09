from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from monitoring.filterset import OfficeCameraFilter
from monitoring.models import OfficeCamera
from monitoring.serializers import OfficeCameraSerializer, OfficeCameraListSerializer


class OfficeCameraFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in OfficeCamera._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class OfficeCameraView(ListCreateAPIView):
    serializer_class = OfficeCameraListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = OfficeCameraFilter
    search_fields = ('object_name', 'direction', 'ip_address', 'address', 'login', 'camera_type')
    ordering = ['-pk']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OfficeCamera.objects.select_related('region', 'district', 'mahalla').all()

    def post(self, request, **kwargs):
        serializer = OfficeCameraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class OfficeCameraDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = OfficeCameraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OfficeCamera.objects.select_related('region', 'district', 'mahalla').all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        obj = get_object_or_404(OfficeCamera, id=pk)
        serializer = OfficeCameraListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = get_object_or_404(OfficeCamera, id=pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)
