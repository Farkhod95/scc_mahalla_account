from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from directory.serializers import RegionListSerializer, DistrictSerializer

from .models import User, Role, AppModule
from .utils.permissions import get_user_permissions


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename']


class RoleSerializer(serializers.ModelSerializer):
    # permissions = Permission.objects.values('id')

    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(style={'input_type': 'username'})
    password = serializers.CharField(style={'input_type': 'password'})



class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source='role', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'first_name', 'last_name', 'second_name',
            'gender', 'date_of_birthday',
            'phone_number', 'email',
            'is_active', 'date_joined',
            'organization', 'department', 'position',
            'region', 'district',
            'role', 'roles',
            'address', 'avatar',
            'pinfl', 'passport_series', 'passport_number',
            'password',
        )
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator(), UniqueValidator(queryset=User.objects.all())],
            },
            'pinfl': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'second_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'avatar': {'required': False, 'allow_null': True},
            'date_of_birthday': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True, 'allow_blank': True},
            'organization': {'required': False, 'allow_null': True},
            'department': {'required': False, 'allow_null': True},
            'position': {'required': False, 'allow_null': True},
            'region': {'required': False, 'allow_null': True},
            'district': {'required': False, 'allow_null': True},
            'role': {'required': False, 'allow_null': True},
            'passport_series': {'required': False, 'allow_blank': True},
            'passport_number': {'required': False, 'allow_blank': True},
        }

    def get_avatar(self, obj):
        """
        Natija:
        - avatar bo'lsa => https://domain.com/assets/avatars/...
        - bo'lmasa => None
        """
        if not obj.avatar:
            return None

        request = self.context.get("request")
        # avatar.url odatda "/assets/..." yoki "/media/..." bo'ladi
        url = obj.avatar.url

        # request bo'lsa to'liq qilib beradi
        if request:
            return request.build_absolute_uri(url)

        # request kelmasa fallback (kamdan-kam holat)
        return url

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListPublicSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source='role', read_only=True)
    region_detail = RegionListSerializer(source='region', read_only=True)
    district_detail = DistrictSerializer(source='district', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'first_name', 'last_name', 'second_name',
            'phone_number', 'email',
            'role', 'roles',
            'region', 'district',
            'region_detail', 'district_detail',
            'avatar',
        )


class UserListSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source='role', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'first_name', 'last_name', 'second_name',
            'gender', 'date_of_birthday',
            'phone_number', 'email',
            'is_active', 'date_joined',
            'role', 'roles',
            'region', 'district',
            'organization', 'department', 'position',
            'avatar',
            'pinfl', 'passport_series', 'passport_number',
        )

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(obj.avatar.url)
                # HTTP ni HTTPS ga o'zgartirish
                return url.replace('http://', 'https://')
            return obj.avatar.url
        return None

class UserUpdateBySerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source='role', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'first_name', 'last_name', 'second_name',
            'gender', 'date_of_birthday',
            'phone_number', 'email',
            'is_active',
            'role', 'roles',
            'region', 'district',
            'organization', 'department', 'position',
            'address', 'avatar',
            'pinfl', 'passport_series', 'passport_number',
            'password',
        )

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RelatedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator(), UniqueValidator(queryset=User.objects.all())],
            }
        }


class RelatedUserPutSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'username': {
                'validators': [],
            }
        }


class ContentTypeSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField(method_name='get_permissions')

    class Meta:
        model = ContentType
        fields = ('id', 'model', 'permissions')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if hasattr(instance, 'extendedcontenttype'):
            ret['model'] = instance.extendedcontenttype.extend_name.upper()
        else:
            ret['model'] = ret['model'].upper()
        return ret

    def get_permissions(self, instance):
        permissions = Permission.objects.filter(content_type=instance.id)
        result = []
        for p in permissions:
            result.append(
                {"id": p.id, "name": p.codename.split('_')[0].upper()}
            )
        return result


class AppModuleSerializer(serializers.ModelSerializer):
    modules = ContentTypeSerializer(source='content_types', read_only=True, many=True)

    class Meta:
        model = AppModule
        fields = ('id', 'name', 'modules', 'sorting')


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()
        return instance
