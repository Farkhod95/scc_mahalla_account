from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.filterset import ShopTenantFilter
from monitoring.models import ShopTenant
from monitoring.serializer.shop_tenant import ShopTenantSerializer, ShopTenantListSerializer
from restapp.pagination import ResultsSetPagination


class ShopTenantFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in ShopTenant._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None,
            })
        return Response(field_info, status=status.HTTP_200_OK)


class ShopTenantView(ListCreateAPIView):
    serializer_class = ShopTenantListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ShopTenantFilter
    search_fields = ('name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'stir', 'certificate_number', 'cash_register_number')
    ordering_fields = ('pk', 'shop', 'rented_area', 'employees_count', 'monthly_checks_count', 'daily_checks_count', 'monthly_visitors', 'daily_visitors')
    ordering = ('-pk',)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShopTenant.objects.select_related('shop').order_by('-pk')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShopTenantSerializer
        return ShopTenantListSerializer

    def post(self, request, *args, **kwargs):
        serializer = ShopTenantSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShopTenantDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ShopTenantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShopTenant.objects.select_related('shop').all()

    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ShopTenantListSerializer(obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ShopTenantSerializer(obj, data=request.data, partial=False, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def patch(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ShopTenantSerializer(obj, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        obj.delete()
        return Response({"detail": "Shop tenant muvaffaqiyatli o‘chirildi."}, status=status.HTTP_204_NO_CONTENT)