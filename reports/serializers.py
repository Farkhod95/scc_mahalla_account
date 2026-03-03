from rest_framework import serializers


class DetectionCountQuerySerializer(serializers.Serializer):
    ip_address = serializers.IPAddressField(required=True)
    region_soato = serializers.IntegerField(required=True, min_value=1)

    # Siz yuborgan format: "25.02.2026 00:00:00"
    from_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])
    to_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])


class FaceDetectionCountQuerySerializer(serializers.Serializer):
    region_soato = serializers.IntegerField(required=True, min_value=1)
    ip_address = serializers.IPAddressField(required=True)

    from_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])
    to_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])
