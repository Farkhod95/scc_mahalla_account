from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.response import Response

from directory.filterset import GomFilter
from directory.models import Gom
from directory.serializers import GomListSerializer, GomSerializer

from restapp.pagination import ResultsSetPagination


class GomView(ListCreateAPIView):
    serializer_class = GomListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = GomFilter
    search_fields = ('name_ru', 'name_en', 'name_uz', 'code')
    ordering = ['pk']

    def get_queryset(self):
        queryset = Gom.objects.all()
        district_ids = self.request.GET.get('district')
        if district_ids is not None:
            try:
                districts = [int(id) for id in district_ids.split(',')]
                queryset = queryset.filter(district__in=districts)
            except ValueError:
                raise APIException("ID is not number")
        return queryset

    def post(self, request):
        serializer = GomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class GomDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GomSerializer

    def get_queryset(self):
        return Gom.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(Gom, id=pk)
        serializer = GomListSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(Gom, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

