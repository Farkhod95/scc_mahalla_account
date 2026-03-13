from rest_framework import serializers

from monitoring.models import ShopTenant


class ShopTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopTenant
        fields = ('id', 'shop', 'rented_area', 'business_type', 'tax_type', 'activity_status', 'name', 'leader_fio',
                  'leader_jshshir', 'leader_phone', 'avatar', 'stir', 'certificate_number', 'employees_count',
                  'cash_register_number', 'ytd_okkm', 'ytd_e_invoice', 'ytd_qr', 'mtd_okkm', 'mtd_e_invoice', 'mtd_qr',
                  'dtd_okkm', 'dtd_e_invoice', 'dtd_qr', 'monthly_checks_count', 'daily_checks_count', 'monthly_visitors',
                  'daily_visitors', 'fire_safety_level', 'has_fire_alarm', 'extinguisher_info', 'is_red_category', 'red_reason')
        # extra_kwargs = {
        #     'shop': {'required': False, 'allow_null': True},
        #     'rented_area': {'required': False, 'allow_null': True},
        #     'business_type': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'tax_type': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'activity_status': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'name': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'leader_fio': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'leader_jshshir': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'leader_phone': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'stir': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'certificate_number': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'employees_count': {'required': False, 'allow_null': True},
        #     'cash_register_number': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'ytd_okkm': {'required': False, 'allow_null': True},
        #     'ytd_e_invoice': {'required': False, 'allow_null': True},
        #     'ytd_qr': {'required': False, 'allow_null': True},
        #     'mtd_okkm': {'required': False, 'allow_null': True},
        #     'mtd_e_invoice': {'required': False, 'allow_null': True},
        #     'mtd_qr': {'required': False, 'allow_null': True},
        #     'dtd_okkm': {'required': False, 'allow_null': True},
        #     'dtd_e_invoice': {'required': False, 'allow_null': True},
        #     'dtd_qr': {'required': False, 'allow_null': True},
        #     'monthly_checks_count': {'required': False, 'allow_null': True},
        #     'daily_checks_count': {'required': False, 'allow_null': True},
        #     'monthly_visitors': {'required': False, 'allow_null': True},
        #     'daily_visitors': {'required': False, 'allow_null': True},
        #     'fire_safety_level': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'extinguisher_info': {'required': False, 'allow_null': True, 'allow_blank': True},
        #     'red_reason': {'required': False, 'allow_null': True, 'allow_blank': True},
        # }


class ShopTenantListSerializer(serializers.ModelSerializer):
    business_type_label = serializers.CharField(source='get_business_type_display', read_only=True)
    tax_type_label = serializers.CharField(source='get_tax_type_display', read_only=True)
    activity_status_label = serializers.CharField(source='get_activity_status_display', read_only=True)
    fire_safety_level_label = serializers.CharField(source='get_fire_safety_level_display', read_only=True)
    shop_id = serializers.IntegerField(source='shop.id', read_only=True)
    shop_number = serializers.CharField(source='shop.shop_number', read_only=True)
    shop_block_type = serializers.CharField(source='shop.block_type', read_only=True)
    shop_block_type_label = serializers.CharField(source='shop.get_block_type_display', read_only=True)

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = ShopTenant
        fields = ('id', 'shop', 'shop_id', 'shop_number', 'shop_block_type', 'shop_block_type_label', 'rented_area',
                  'business_type', 'business_type_label', 'tax_type', 'tax_type_label', 'activity_status',
                  'activity_status_label', 'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'avatar', 'stir',
                  'certificate_number', 'employees_count', 'cash_register_number', 'ytd_okkm', 'ytd_e_invoice', 'ytd_qr',
                  'mtd_okkm', 'mtd_e_invoice', 'mtd_qr', 'dtd_okkm', 'dtd_e_invoice', 'dtd_qr', 'monthly_checks_count',
                  'daily_checks_count', 'monthly_visitors', 'daily_visitors', 'fire_safety_level',
                  'fire_safety_level_label', 'has_fire_alarm', 'extinguisher_info', 'is_red_category', 'red_reason')

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