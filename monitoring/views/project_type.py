from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response

from monitoring.filterset import ProjectTypeFilter
from monitoring.models import ProjectType
from monitoring.serializers import ProjectTypeSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class ProjectTypeView(ListCreateAPIView):
    serializer_class = ProjectTypeSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ProjectTypeFilter
    search_fields = ('name_en', 'name_ru', 'name_uz',)
    ordering = ['pk']

    def get_queryset(self):
        return ProjectType.objects.all()

    def post(self, request):
        serializer = ProjectTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ProjectTypeDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectTypeSerializer

    def get_queryset(self):
        return ProjectType.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(ProjectType, id=pk)
        serializer = ProjectTypeSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(ProjectType, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(ProjectType, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



