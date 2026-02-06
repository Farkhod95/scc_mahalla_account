from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.filterset import PositionFilter
from directory.models import Position
from directory.serializers import PositionSerializer, PositionListSerializer

from restapp.pagination import ResultsSetPagination
from rest_framework.permissions import AllowAny


class PositionFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []

        for field in Position._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class PositionPublicView(ListCreateAPIView):
    serializer_class = PositionListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = PositionFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['-pk']
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get_queryset(self):
        return Position.objects.all()


class PositionDetailPublicView(APIView):
    serializer_class = PositionSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get(self, request, pk):
        position = get_object_or_404(Position, id=pk)
        serializer = PositionListSerializer(position)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PositionView(ListCreateAPIView):
    serializer_class = PositionListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = PositionFilter
    search_fields = ('name_ru', 'name_en', 'name_uz')
    ordering = ['-pk']

    def get_queryset(self):
        return Position.objects.all()

    def post(self, request, **kwargs):
        serializer = PositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class PositionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PositionSerializer

    def get_queryset(self):
        return Position.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        position = get_object_or_404(Position, id=pk)
        serializer = PositionListSerializer(position)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        position = get_object_or_404(Position, id=pk)
        serializer = self.serializer_class(position, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)
