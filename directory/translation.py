from modeltranslation.translator import register, TranslationOptions
from .models import Region, District, Mahalla, Organization, Department, Position, Gom


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(District)
class DistrictTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Gom)
class GomTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Mahalla)
class MahallaTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Organization)
class OrganizationTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Position)
class PositionTranslationOptions(TranslationOptions):
    fields = ('name',)