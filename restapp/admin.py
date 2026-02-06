from django.contrib import admin

from django.contrib.contenttypes.models import ContentType
from restapp.models import TranslationTerm, ExtendedContentType


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, instance, form, change):
        if instance.id is None:
            instance.created_by_id = request.user.id
        instance.updated_by_id = request.user.id
        instance.save()


@admin.register(TranslationTerm)
class UILanguageAdmin(BaseAdmin):
    list_display = ('id', 'term_name', 'name_en', 'name_ru', 'name_uz')
    fields = ('term_name', 'name_en', 'name_ru', 'name_uz')


class ExtendedContentTypeInline(admin.TabularInline):
    model = ExtendedContentType


@admin.register(ContentType)
class ContentType(BaseAdmin):
    ordering = ['app_label']
    list_display = ('id', 'app_label', 'model', 'extend_name')
    fields = ('app_label', 'model')
    inlines = [ExtendedContentTypeInline, ]

    def extend_name(self, instance):
        return instance.extendedcontenttype.extend_name