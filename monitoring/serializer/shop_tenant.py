from rest_framework import serializers
from monitoring.models import ShopTenant
from monitoring.serializer.shop import ShopListSerializer  # ShopListSerializer qayerda bo'lsa importni moslang


class ShopTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopTenant
        fields = ('id', 'shop', 'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'avatar', 'stir', 'certificate_number', 'employees_count')
        extra_kwargs = {
            'shop': {"required": True},
            'name': {"required": False, "allow_null": True, "allow_blank": True},
            'leader_fio': {"required": False, "allow_null": True, "allow_blank": True},
            'leader_jshshir': {"required": False, "allow_null": True, "allow_blank": True},
            'leader_phone': {"required": False, "allow_null": True, "allow_blank": True},
            'stir': {"required": False, "allow_null": True, "allow_blank": True},
            'certificate_number': {"required": False, "allow_null": True, "allow_blank": True},
            'employees_count': {"required": False, "allow_null": True},
        }


class ShopTenantListSerializer(serializers.ModelSerializer):
    shop_detail = ShopListSerializer(source='shop', read_only=True)

    class Meta:
        model = ShopTenant
        fields = ('id', 'shop', 'shop_detail', 'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'avatar', 'stir', 'certificate_number', 'employees_count')