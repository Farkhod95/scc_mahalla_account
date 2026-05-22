from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import ShopCrime
from monitoring.serializer.shop_crime import ShopCrimeSerializer


class ShopCrimeListCreateView(APIView):
    """
    GET  /shop-crime/          — barcha jinoyatlar ro'yxati
    POST /shop-crime/          — yangi jinoyat yaratish (shop, malika_bozor, content)
    GET  /shop-crime/?shop_id= — bitta do'kon jinoyatlari
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ShopCrime.objects.select_related('shop')
        shop_id = request.query_params.get('shop_id')
        if shop_id:
            qs = qs.filter(shop_id=shop_id)
        serializer = ShopCrimeSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShopCrimeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShopCrimeDetailView(APIView):
    """
    GET    /shop-crime/<id>  — bitta jinoyat
    PUT    /shop-crime/<id>  — to'liq yangilash
    PATCH  /shop-crime/<id>  — qisman yangilash
    DELETE /shop-crime/<id>  — o'chirish
    """
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk):
        return get_object_or_404(ShopCrime.objects.select_related('shop'), pk=pk)

    def get(self, request, pk):
        serializer = ShopCrimeSerializer(self._get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        obj = self._get_object(pk)
        serializer = ShopCrimeSerializer(obj, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        obj = self._get_object(pk)
        serializer = ShopCrimeSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        self._get_object(pk).delete()
        return Response({"detail": "O'chirildi."}, status=status.HTTP_204_NO_CONTENT)
