from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response

from monitoring.filterset import DeviceTypeFilter
from monitoring.models import DeviceType
from monitoring.serializers import DeviceTypeSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class DeviceTypeView(ListCreateAPIView):
    serializer_class = DeviceTypeSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DeviceTypeFilter
    search_fields = ('name', 'name_en', 'name_ru' ,'name_uz', 'key',)
    ordering = ['-pk']

    def get_queryset(self):
        return DeviceType.objects.all()

    def post(self, request):
        serializer = DeviceTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class DeviceTypeDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DeviceTypeSerializer

    def get_queryset(self):
        return DeviceType.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(DeviceType, id=pk)
        serializer = DeviceTypeSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(DeviceType, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(DeviceType, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



