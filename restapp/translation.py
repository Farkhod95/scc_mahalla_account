from modeltranslation.translator import register, TranslationOptions
from .models import TranslationTerm


@register(TranslationTerm)
class TermTranslationOptions(TranslationOptions):
    fields = ('name',)