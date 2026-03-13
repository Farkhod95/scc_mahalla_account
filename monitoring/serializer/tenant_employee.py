from rest_framework import serializers
from monitoring.models import TenantEmployee
from monitoring.serializer.shop_tenant import ShopTenantListSerializer  # ShopTenantListSerializer qayerda bo'lsa importni moslang


class TenantEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantEmployee
        fields = ('id', 'tenant', 'fio', 'jshshir', 'phone', 'avatar')
        extra_kwargs = {
            'tenant': {"required": True},
            'fio': {"required": False, "allow_null": True, "allow_blank": True},
            'jshshir': {"required": False, "allow_null": True, "allow_blank": True},
            'phone': {"required": False, "allow_null": True, "allow_blank": True},
        }


class TenantEmployeeListSerializer(serializers.ModelSerializer):
    tenant_detail = ShopTenantListSerializer(source='tenant', read_only=True)

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = TenantEmployee
        fields = ('id', 'tenant', 'tenant_detail', 'fio', 'jshshir', 'phone', 'avatar')


    def get_avatar(self, obj):
        if not obj.avatar:
            return None

        request = self.context.get('request')
        if not request:
            # request bo'lmasa ham kamida fayl url qaytadi
            return obj.avatar.url

        url = request.build_absolute_uri(obj.avatar.url)

        # Agar build_absolute_uri http qilib bersa, majburan https ga o'tkazamiz
        # (Ko'p holatda reverse proxy/ssl terminator sabab bo'ladi)
        return url.replace('http://', 'https://', 1)