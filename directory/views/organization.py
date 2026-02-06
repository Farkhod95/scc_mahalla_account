from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.filterset import OrganizationFilter
from directory.models import Organization
from directory.serializers import OrganizationSerializer, OrganizationListSerializer
from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class OrganizationFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []

        for field in Organization._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class OrganizationView(ListCreateAPIView):
    serializer_class = OrganizationListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = OrganizationFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['pk']

    def get_queryset(self):
        return Organization.objects.all()

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class OrganizationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(Organization, id=pk)
        serializer = OrganizationListSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(Organization, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(Organization, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



