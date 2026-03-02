from rest_framework import serializers
from monitoring.models import ShopCamera
from monitoring.serializer.shop import ShopListSerializer  # agar ShopListSerializer shu modulda bo'lsa; bo'lmasa import yo'lini moslang


class ShopCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCamera
        fields = ('id', 'shop', 'url')
        extra_kwargs = {
            'shop': {"required": True},
            'url': {"required": False, "allow_null": True, "allow_blank": True},
        }


class ShopCameraListSerializer(serializers.ModelSerializer):
    shop_detail = ShopListSerializer(source='shop', read_only=True)

    class Meta:
        model = ShopCamera
        fields = ('id', 'shop', 'shop_detail', 'url')