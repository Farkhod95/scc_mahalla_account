from rest_framework import serializers

from monitoring.models import ShopCrime


class ShopCrimeSerializer(serializers.ModelSerializer):
    shop_display = serializers.StringRelatedField(source='shop', read_only=True)

    class Meta:
        model = ShopCrime
        fields = ('id', 'shop', 'shop_display', 'malika_bozor', 'date', 'content', 'created_time', 'updated_time')
        extra_kwargs = {
            'shop': {'required': True},
            'content': {'required': True},
            'malika_bozor': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
