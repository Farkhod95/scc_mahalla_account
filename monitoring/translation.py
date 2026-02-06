from modeltranslation.translator import register, TranslationOptions
from monitoring.models import ObjectCategory, CrimeCategory


@register(ObjectCategory)
class ObjectCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(CrimeCategory)
class CrimeCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)