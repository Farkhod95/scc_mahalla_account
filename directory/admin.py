from django.contrib import admin

from directory.models import District, Region, Mahalla, Organization, Department, Position


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code',)
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'center_x', 'center_y', 'zoom', 'geo_json',)
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'geo_json', 'center_x', 'center_y', 'zoom')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code')
    list_filter = ('region',)


@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_district_code', 'region', 'district')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'district', 'geo_json', 'center_x', 'center_y', 'zoom')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code')
    list_filter = ('region', 'district')

    @admin.display(description="District code")  # Django 3.2+
    def get_district_code(self, obj):
        return obj.district.code if obj.district else "-"



@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'district')
    fields = ('name', 'name_en', 'name_ru', 'name_uz', 'code', 'region', 'district')
    search_fields = ('name', 'name_en', 'name_ru', 'name_uz')
    autocomplete_fields = ('region', 'district')


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

