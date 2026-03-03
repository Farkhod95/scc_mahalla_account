from rest_framework import serializers
from monitoring.models import BazarCamera


class BazarCameraSerializer(serializers.ModelSerializer):

    class Meta:
        model = BazarCamera
        fields = ('id', 'object_name', 'type', 'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol')


class BazarCameraListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BazarCamera
        fields = ('id', 'object_name', 'type', 'coordinate_x', 'coordinate_y', 'url', 'icon', 'login', 'parol')