from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from monitoring.filterset import ShopTradeStatsFilter
from monitoring.models import ShopTradeStats
from monitoring.serializer.shop_trade_stats import ShopTradeStatsSerializer, ShopTradeStatsListSerializer


class ShopTradeStatsFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []
        for field in ShopTradeStats._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })
        return Response(field_info)


class ShopTradeStatsView(ListCreateAPIView):
    serializer_class = ShopTradeStatsListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ShopTradeStatsFilter
    search_fields = ('shop__code', 'shop__owner_fio', 'cash_register_number', 'red_reason')
    ordering_fields = ('pk', 'shop', 'monthly_visitors', 'daily_visitors', 'monthly_checks_count', 'daily_checks_count', 'ytd_okkm', 'mtd_okkm', 'dtd_okkm')
    ordering = ['-pk']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShopTradeStats.objects.select_related('shop').all()

    def post(self, request, **kwargs):
        serializer = ShopTradeStatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ShopTradeStatsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ShopTradeStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShopTradeStats.objects.select_related('shop').all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        obj = get_object_or_404(ShopTradeStats, id=pk)
        serializer = ShopTradeStatsListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = get_object_or_404(ShopTradeStats, id=pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)