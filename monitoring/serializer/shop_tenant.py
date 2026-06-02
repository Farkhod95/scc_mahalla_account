from rest_framework import serializers

from monitoring.models import ShopTenant
from monitoring.services import soliq_service


class SoliqEnrichMixin:
    """
    Serializer chiqishini (representation) soliq integratsiyasidan kelgan
    qiymatlar bilan to'ldiradi. Maydon nomlari o'zgarmaydi — frontend o'zgarmaydi.
    Soliq ochilmasa/xato bo'lsa, bazadagi qiymat saqlanib qoladi.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)
        overlay = soliq_service.soliq_fields_for(getattr(instance, "leader_jshshir", None))
        for key, value in overlay.items():
            if key in data:
                data[key] = value
        # activity_status o'zgargan bo'lsa, label ni ham yangilaymiz
        if "activity_status" in overlay and "activity_status_label" in data:
            data["activity_status_label"] = dict(ShopTenant.ActivityStatus.choices).get(
                overlay["activity_status"], data["activity_status_label"]
            )

        # Faktura tushumi (e_payment) — og'ir bo'lgani uchun faqat detalda.
        if self.context.get("include_factura"):
            tin = overlay.get("stir") or getattr(instance, "stir", None)
            factura = soliq_service.factura_turnover_fields(tin, getattr(instance, "tax_type", None))
            for key, value in factura.items():
                if key in data:
                    data[key] = value

        return data


class ShopTenantSerializer(SoliqEnrichMixin, serializers.ModelSerializer):
    class Meta:
        model = ShopTenant
        fields = ('id', 'shop', 'rented_area', 'business_type', 'tax_type', 'trade_type', 'activity_status', 'name', 'leader_fio',
                  'leader_jshshir', 'leader_phone', 'avatar', 'stir', 'certificate_number', 'employees_count',
                  'cash_register_number_vat', 'cash_register_number_turnover',
                  'ytd_okkm_vat', 'ytd_okkm_turnover', 'ytd_e_payment_vat', 'ytd_e_payment_turnover',
                  'mtd_okkm_vat', 'mtd_okkm_turnover', 'mtd_e_payment_vat', 'mtd_e_payment_turnover',
                  'dtd_okkm_vat', 'dtd_okkm_turnover', 'dtd_e_payment_vat', 'dtd_e_payment_turnover',
                  'monthly_checks_count_vat', 'monthly_checks_count_turnover',
                  'daily_checks_count_vat', 'daily_checks_count_turnover',
                  'monthly_visitors', 'daily_visitors', 'fire_safety_level', 'has_fire_alarm', 'extinguisher_info',
                  'is_red_category', 'red_reason')
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


class ShopTenantListSerializer(SoliqEnrichMixin, serializers.ModelSerializer):
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
                  'business_type', 'business_type_label', 'tax_type', 'tax_type_label', 'trade_type', 'activity_status',
                  'activity_status_label', 'name', 'leader_fio', 'leader_jshshir', 'leader_phone', 'avatar', 'stir',
                  'certificate_number', 'employees_count',
                  'cash_register_number_vat', 'cash_register_number_turnover',
                  'ytd_okkm_vat', 'ytd_okkm_turnover', 'ytd_e_payment_vat', 'ytd_e_payment_turnover',
                  'mtd_okkm_vat', 'mtd_okkm_turnover', 'mtd_e_payment_vat', 'mtd_e_payment_turnover',
                  'dtd_okkm_vat', 'dtd_okkm_turnover', 'dtd_e_payment_vat', 'dtd_e_payment_turnover',
                  'monthly_checks_count_vat', 'monthly_checks_count_turnover',
                  'daily_checks_count_vat', 'daily_checks_count_turnover',
                  'monthly_visitors', 'daily_visitors', 'fire_safety_level',
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
        return url.replace('http://', 'http://', 1)