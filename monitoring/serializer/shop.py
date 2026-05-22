from rest_framework import serializers

from monitoring.models import Shop, ShopCamera


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'block_type', 'shop_number', 'code', 'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone', 'avatar', 'total_area', 'tenants_count')
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
    is_red_category = serializers.SerializerMethodField()
    is_crime = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    actual_tenants_count = serializers.SerializerMethodField()
    cameras_count = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = (
            'id', 'block_type', 'block_type_label', 'code', 'shop_number',
            'owner_company_name', 'owner_fio', 'owner_jshshir', 'owner_phone',
            'avatar', 'total_area', 'tenants_count', 'actual_tenants_count',
            'cameras_count', 'shop_cameras', 'is_red_category', 'is_crime',
        )

    def get_avatar(self, obj):
        if not obj.avatar:
            return None

        request = self.context.get('request')
        if not request:
            return obj.avatar.url

        url = request.build_absolute_uri(obj.avatar.url)
        return url.replace('http://', 'http://', 1)

    def get_is_red_category(self, obj):
        return obj.tenants.filter(is_red_category=True).exists()

    def get_is_crime(self, obj):
        return obj.crimes.exists()

    def get_actual_tenants_count(self, obj):
        return obj.tenants.count()

    def get_cameras_count(self, obj):
        return obj.shop_cameras.count()