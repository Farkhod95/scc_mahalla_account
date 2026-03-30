from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from monitoring.filterset import MFYCitizenFilter
from monitoring.models import MFYCitizen
from monitoring.serializer.mfy_citizen import MFYCitizenSerializer, MFYCitizenListSerializer


class MFYCitizenFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in MFYCitizen._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class MFYCitizenView(ListCreateAPIView):
    serializer_class = MFYCitizenListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = MFYCitizenFilter
    search_fields = ('full_name', 'phone', 'address')
    ordering = ['-pk']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MFYCitizen.objects.select_related(
            'region', 'district', 'mahalla'
        ).all()

    def post(self, request, *args, **kwargs):
        serializer = MFYCitizenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MFYCitizenDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = MFYCitizenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MFYCitizen.objects.select_related(
            'region', 'district', 'mahalla'
        ).all()

    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = MFYCitizenListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def patch(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        obj.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)