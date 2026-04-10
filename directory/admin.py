from django.contrib import admin

from directory.models import District, Region, Mahalla, Organization, Department, Position, Gom


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'center_x', 'center_y', 'zoom', 'geo_json', 'is_active')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'is_active')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'is_active')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'geo_json', 'center_x', 'center_y', 'zoom', 'is_active')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code')
    list_filter = ('region', 'is_active',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            kwargs["queryset"] = Region.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_district_code', 'region', 'district', 'gom', 'is_active')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'district', 'gom', 'geo_json', 'center_x', 'center_y', 'zoom', 'is_active')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code')
    list_filter = ('region', 'district', 'gom', 'is_active')

    @admin.display(description="District code")  # Django 3.2+
    def get_district_code(self, obj):
        return obj.district.code if obj.district else "-"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            kwargs["queryset"] = Region.objects.filter(is_active=True)
        elif db_field.name == "district":
            kwargs["queryset"] = District.objects.filter(is_active=True)
        elif db_field.name == "gom":
            kwargs["queryset"] = Gom.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Gom)
class GomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_district_code', 'region', 'district', 'is_active')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'district', 'is_active')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code')
    list_filter = ('region', 'district', 'is_active')

    @admin.display(description="District code")  # Django 3.2+
    def get_district_code(self, obj):
        return obj.district.code if obj.district else "-"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            kwargs["queryset"] = Region.objects.filter(is_active=True)
        elif db_field.name == "district":
            kwargs["queryset"] = District.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'district', 'mahalla', 'gom')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'district', 'mahalla', 'gom')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')
    autocomplete_fields = ('region', 'district', 'mahalla', 'gom')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ru', 'name_uz', 'organization')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'organization')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'name_en', 'name_ru', 'name_uz')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'department')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')

