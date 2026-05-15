from django.utils import timezone
from rest_framework import serializers
from monitoring.models import CarFlow, BazarCamera


class CarFlowCreateSerializer(serializers.ModelSerializer):
    region_soato = serializers.IntegerField(required=True)
    recorded_at = serializers.DateTimeField(required=False)

    class Meta:
        model = CarFlow
        fields = ['ip_address', 'location_type', 'region_soato', 'type', 'recorded_at']

    def create(self, validated_data):
        if 'recorded_at' not in validated_data:
            validated_data['recorded_at'] = timezone.now()
        ip = validated_data['ip_address']
        location = validated_data.get('location_type')
        camera = BazarCamera.objects.filter(ip_address=ip, location_type=location).first()
        return CarFlow.objects.create(camera=camera, **validated_data)


class CarFlowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFlow
        fields = ['id', 'ip_address', 'location_type', 'region_soato', 'type', 'recorded_at', 'created_time']
