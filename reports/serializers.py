from rest_framework import serializers


class DetectionCountQuerySerializer(serializers.Serializer):
    ip_address = serializers.IPAddressField(required=True)
    region_soato = serializers.IntegerField(required=True, min_value=1)

    # Siz yuborgan format: "25.02.2026 00:00:00"
    from_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])
    to_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])


class FaceDetectionCountQuerySerializer(serializers.Serializer):
    region_soato = serializers.IntegerField(required=True)
    ip_address = serializers.CharField(required=True)  # kamera IP bo‘lishi mumkin
    from_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])
    to_dt = serializers.DateTimeField(required=True, input_formats=["%d.%m.%Y %H:%M:%S"])


class MalikaFlowQuerySerializer(serializers.Serializer):
    region_soato = serializers.IntegerField(required=True)
    from_date = serializers.DateTimeField(
        required=True,
        input_formats=["%d.%m.%Y %H:%M:%S"],  # 2026-02-25 00:00:00
    )
    to_date = serializers.DateTimeField(
        required=True,
        input_formats=["%d.%m.%Y %H:%M:%S"],  # 2026-02-25 23:59:59
    )
