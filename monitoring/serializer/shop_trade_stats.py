from rest_framework import serializers
from monitoring.models import ShopTradeStats
from monitoring.serializer.shop import ShopListSerializer  # ShopListSerializer qayerda bo'lsa moslang


class ShopTradeStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopTradeStats
        fields = ('id', 'shop', 'tax_type', 'cash_register_number', 'ytd_okkm', 'ytd_e_invoice', 'ytd_qr', 'mtd_okkm', 'mtd_e_invoice', 'mtd_qr', 'dtd_okkm', 'dtd_e_invoice', 'dtd_qr', 'monthly_checks_count', 'daily_checks_count', 'monthly_visitors', 'daily_visitors', 'activity_status', 'fire_safety_level', 'has_fire_alarm', 'extinguisher_info', 'is_red_category', 'red_reason')
        extra_kwargs = {
            'shop': {"required": True},
            'tax_type': {"required": False, "allow_null": True, "allow_blank": True},
            'cash_register_number': {"required": False, "allow_null": True, "allow_blank": True},
            'activity_status': {"required": False, "allow_null": True, "allow_blank": True},
            'fire_safety_level': {"required": False, "allow_null": True, "allow_blank": True},
            'extinguisher_info': {"required": False, "allow_null": True, "allow_blank": True},
            'red_reason': {"required": False, "allow_null": True, "allow_blank": True},
        }


class ShopTradeStatsListSerializer(serializers.ModelSerializer):
    shop_detail = ShopListSerializer(source='shop', read_only=True)
    tax_type_label = serializers.CharField(source='get_tax_type_display', read_only=True)
    activity_status_label = serializers.CharField(source='get_activity_status_display', read_only=True)
    fire_safety_level_label = serializers.CharField(source='get_fire_safety_level_display', read_only=True)

    class Meta:
        model = ShopTradeStats
        fields = ('id', 'shop', 'shop_detail', 'tax_type', 'tax_type_label', 'cash_register_number', 'ytd_okkm', 'ytd_e_invoice', 'ytd_qr', 'mtd_okkm', 'mtd_e_invoice', 'mtd_qr', 'dtd_okkm', 'dtd_e_invoice', 'dtd_qr', 'monthly_checks_count', 'daily_checks_count', 'monthly_visitors', 'daily_visitors', 'activity_status', 'activity_status_label', 'fire_safety_level', 'fire_safety_level_label', 'has_fire_alarm', 'extinguisher_info', 'is_red_category', 'red_reason')