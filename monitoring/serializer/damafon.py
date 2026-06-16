from rest_framework import serializers

from monitoring.models import DamafonCall


class DamafonCallSerializer(serializers.ModelSerializer):
    # WS broadcast va REST bir xil shaklda bo'lishi uchun: damafon_id <- remote_damafon_id.
    damafon_id = serializers.IntegerField(source="remote_damafon_id", allow_null=True, read_only=True)

    class Meta:
        model = DamafonCall
        fields = ("id", "damafon_id", "damafon_name", "host", "call_id",
                  "stream", "location_id", "received_at")
