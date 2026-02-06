from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from monitoring.filterset import DeviceLogFilter
from monitoring.models import DeviceLog, Device
from monitoring.serializers import DeviceLogSerializer, DeviceLogListSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class DeviceLogView(ListCreateAPIView):
    serializer_class = DeviceLogListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DeviceLogFilter
    search_fields = ('id')
    ordering = ['-pk']

    def get_queryset(self):
        return DeviceLog.objects.all()

    def post(self, request):
        serializer = DeviceLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class DeviceLogDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DeviceLogSerializer

    def get_queryset(self):
        return DeviceLog.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(DeviceLog, id=pk)
        serializer = DeviceLogListSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(DeviceLog, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(DeviceLog, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



