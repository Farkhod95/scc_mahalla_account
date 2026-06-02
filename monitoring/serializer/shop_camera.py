from rest_framework import serializers
from monitoring.models import ShopCamera
from monitoring.serializer.shop import ShopListSerializer
from monitoring.services import go2rtc_service


class ShopCameraSerializer(serializers.ModelSerializer):
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopCamera
        fields = ('id', 'shop', 'title', 'url', 'stream_url')
        extra_kwargs = {
            'shop': {"required": True},
            'url': {"required": False, "allow_null": True, "allow_blank": True},
        }

    def get_stream_url(self, obj):
        return go2rtc_service.get_webrtc_url(obj)


class ShopCameraListSerializer(serializers.ModelSerializer):
    shop_detail = ShopListSerializer(source='shop', read_only=True)
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopCamera
        fields = ('id', 'shop', 'title', 'shop_detail', 'url', 'stream_url')

    def get_stream_url(self, obj):
        return go2rtc_service.get_webrtc_url(obj)