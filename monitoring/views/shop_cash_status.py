"""
Do'kon kassa (onlayn-NKM/chek) faolligi rangi (qizil/sariq/yashil) — xarita uchun.

GET /shop/cash-status/             -> barcha do'konlar
GET /shop/cash-status/?shop=<id>   -> bitta do'kon
GET /shop/cash-status/?block_type=A
"""
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import Shop
from monitoring.services.shop_status import shop_cash_status


def _row(shop):
    return {
        "shop_id": shop.id,
        "code": shop.code,
        "block_type": shop.block_type,
        "shop_number": shop.shop_number,
        **shop_cash_status(shop),
    }


class ShopCashStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop_id = request.query_params.get("shop")
        block_type = request.query_params.get("block_type")

        if shop_id:
            shop = get_object_or_404(Shop, pk=shop_id)
            return Response(_row(shop))

        qs = Shop.objects.prefetch_related("tenants").all()
        if block_type:
            qs = qs.filter(block_type=block_type)

        return Response([_row(shop) for shop in qs])
