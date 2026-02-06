from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response

from monitoring.filterset import ObjectFilter
from monitoring.models import Object
from monitoring.serializers import ObjectSerializer
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class ObjectView(ListCreateAPIView):
    serializer_class = ObjectSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ObjectFilter
    search_fields = ('year')
    ordering = ['pk']

    def get_queryset(self):
        return Object.objects.all()

    def post(self, request):
        serializer = ObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ObjectDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ObjectSerializer

    def get_queryset(self):
        return Object.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(Object, id=pk)
        serializer = ObjectSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(Object, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(Object, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)


class UpdateObjectLocationAPIView(APIView):
    def post(self, request):
        updated = 0
        skipped = 0

        objects = Object.objects.exclude(coordinate_x=None).exclude(coordinate_y=None)

        for object in objects.iterator():  # iterator - katta dataset uchun samarali
            try:
                lat = float(object.coordinate_x)
                lon = float(object.coordinate_y)
                object.save(update_fields=['location'])
                updated += 1
            except Exception as e:
                skipped += 1

        return Response({
            'success': True,
            'updated_count': updated,
            'skipped_count': skipped,
        }, status=status.HTTP_200_OK)



