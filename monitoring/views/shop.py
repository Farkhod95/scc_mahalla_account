from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.filterset import ShopFilter
from monitoring.models import Shop
from monitoring.serializer.shop import ShopSerializer, ShopListSerializer
from restapp.pagination import ResultsSetPagination


class ShopFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in Shop._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None,
            })
        return Response(field_info, status=status.HTTP_200_OK)


class ShopView(ListCreateAPIView):
    serializer_class = ShopListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ShopFilter
    search_fields = ('code', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone', 'shop_number')
    ordering_fields = ('block_type', 'shop_number', 'total_area', 'tenants_count', 'pk')
    ordering = ('block_type', 'shop_number')
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shop.objects.prefetch_related('shop_cameras').order_by('block_type', 'shop_number')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShopSerializer
        return ShopListSerializer

    def post(self, request, *args, **kwargs):
        serializer = ShopSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShopDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shop.objects.prefetch_related('shop_cameras').all()

    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ShopListSerializer(obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ShopSerializer(obj, data=request.data, partial=False, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def patch(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ShopSerializer(obj, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        obj.delete()
        return Response({"detail": "Shop muvaffaqiyatli o‘chirildi."}, status=status.HTTP_204_NO_CONTENT)