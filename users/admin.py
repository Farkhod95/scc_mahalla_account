from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from users.models import User, Role, AppModule


# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": (("username", "password"),)}),

        (_("Personal info"), {"fields": (
            ("last_name", "first_name", "second_name"),
            ("phone_number", "email"),
            ("gender", "date_of_birthday"),
            ("passport_series", "passport_number"),
            ("pinfl",),
            ("address", "avatar"),
        )}),

        (_("Work info"), {"fields": (
            ("organization", "department"),
            ("position", "role"),
            ("region", "district", "mahalla"),
        )}),

        (_("Permissions"), {"fields": (
            ("is_active", "is_staff", "is_superuser"),
            ("groups", "user_permissions"),
        )}),

        (_("Audit"), {"fields": (
            ("created_time", "updated_time"),
            ("created_by", "updated_by"),
            ("date_joined", "last_login"),
        )}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                ("username",),
                ("last_name", "first_name", "second_name"),
                ("phone_number", "email"),
                ("gender", "date_of_birthday"),
                ("passport_series", "passport_number"),
                ("pinfl",),
                ("organization", "department"),
                ("position", "role"),
                ("region", "district", "mahalla"),
                ("address", "avatar"),
                ("is_active", "is_staff", "is_superuser"),
                ("password1", "password2"),
            ),
        }),
    )

    list_display = ("username", "phone_number", "email", "last_name", "first_name", "role", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "role", "region", "district")
    search_fields = ("username", "phone_number", "email", "first_name", "last_name", "pinfl")
    ordering = ("username",)
    filter_horizontal = ("groups", "user_permissions")

    readonly_fields = ("created_time", "updated_time", "created_by", "updated_by", "date_joined", "last_login")



@admin.register(Role)
class RoleAdmin(GroupAdmin):
    list_display = ('name', 'description', 'type')
    fields = ('name', 'description', 'permissions', 'type')
    search_fields = ('name', 'description', 'type')
    filter_horizontal = ('permissions',)


@admin.register(AppModule)
class AppModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'on_dashboard')


