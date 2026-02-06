from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response

from monitoring.filterset import ProjectStapeFilter
from monitoring.models import ProjectStape
from monitoring.serializers import ProjectStapeSerializer, ProjectStapeListSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class ProjectStapeView(ListCreateAPIView):
    serializer_class = ProjectStapeListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ProjectStapeFilter
    search_fields = ('name_en', 'name_ru', 'name_uz', 'project__name')
    ordering = ['pk']

    def get_queryset(self):
        return ProjectStape.objects.all()

    def post(self, request):
        serializer = ProjectStapeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ProjectStapeDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectStapeSerializer

    def get_queryset(self):
        return ProjectStape.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(ProjectStape, id=pk)
        serializer = ProjectStapeListSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(ProjectStape, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(ProjectStape, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



