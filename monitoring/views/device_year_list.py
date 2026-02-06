from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response

from monitoring.filterset import DeviceYearFilter
from monitoring.models import DeviceYear
from monitoring.serializers import DeviceYearSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class DeviceYearView(ListCreateAPIView):
    serializer_class = DeviceYearSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DeviceYearFilter
    search_fields = ('year')
    ordering = ['pk']

    def get_queryset(self):
        return DeviceYear.objects.all()

    def post(self, request):
        serializer = DeviceYearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class DeviceYearDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DeviceYearSerializer

    def get_queryset(self):
        return DeviceYear.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(DeviceYear, id=pk)
        serializer = DeviceYearSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(DeviceYear, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(DeviceYear, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



