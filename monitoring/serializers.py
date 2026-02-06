from rest_framework import serializers

from directory.serializers import RegionListSerializer, DistrictSerializer
import requests
from datetime import datetime
from users.serializers import UserListPublicSerializer
from django.conf import settings
from rest_framework.exceptions import ValidationError
from users.models import User


class LocaleSerializer(serializers.ModelSerializer):
    name_uz = serializers.CharField(allow_blank=False)
    name_ru = serializers.CharField(allow_blank=False)
    name_en = serializers.CharField(allow_blank=False)

