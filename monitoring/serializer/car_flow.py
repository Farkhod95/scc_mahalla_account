from django.utils import timezone
from rest_framework import serializers
from monitoring.models import CarFlow, BazarCamera


class CarFlowCreateSerializer(serializers.ModelSerializer):
    ip = serializers.CharField(source='ip_address')
    duration = serializers.ChoiceField(source='type', choices=CarFlow.TYPE.choices)
    date = serializers.DateTimeField(source='recorded_at', required=False)

    class Meta:
        model = CarFlow
        fields = ['ip', 'duration', 'date', 'plate', 'image']
        extra_kwargs = {'image': {'write_only': True}}

    def create(self, validated_data):
        if 'recorded_at' not in validated_data:
            validated_data['recorded_at'] = timezone.now()

        ip = validated_data['ip_address']
        camera = BazarCamera.objects.filter(ip_address=ip).first()

        location_type = None
        region_soato = None
        if camera:
            location_type = camera.location_type
            region_code = getattr(camera.region, 'code', None)
            if region_code and str(region_code).isdigit():
                region_soato = int(region_code)

        return CarFlow.objects.create(
            camera=camera,
            location_type=location_type,
            region_soato=region_soato,
            **validated_data,
        )


class CarFlowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFlow
        fields = ['id', 'ip_address', 'location_type', 'region_soato', 'type', 'plate', 'recorded_at', 'created_time']
