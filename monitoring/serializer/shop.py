from rest_framework import serializers

from monitoring.models import Shop, ShopCamera


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'block_type', 'shop_number', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone', 'avatar', 'total_area', 'tenants_count')
        extra_kwargs = {
            'block_type': {'required': False, 'allow_null': True, 'allow_blank': True},
            'shop_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'owner_company_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'owner_fio': {'required': False, 'allow_null': True, 'allow_blank': True},
            'owner_jshshir': {'required': False, 'allow_null': True, 'allow_blank': True},
            'owner_phone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'total_area': {'required': False, 'allow_null': True},
            'tenants_count': {'required': False, 'allow_null': True},
        }


class ShopCameraInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCamera
        fields = ('id', 'url')


class ShopListSerializer(serializers.ModelSerializer):
    block_type_label = serializers.CharField(source='get_block_type_display', read_only=True)
    shop_cameras = ShopCameraInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ('id', 'block_type', 'block_type_label', 'shop_number', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone', 'avatar', 'total_area', 'tenants_count', 'shop_cameras')