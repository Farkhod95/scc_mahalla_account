from django.db import models
from django.utils.translation import gettext_lazy as _

from restapp.models import BaseModel


class Region(BaseModel):
    code = models.CharField(_('Region code'), max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    geo_json = models.TextField(_('GeoJson'), blank=True)
    center_x = models.FloatField(blank=True, null=True)
    center_y = models.FloatField(blank=True, null=True)
    zoom = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')

    def __str__(self):
        return self.name


class District(BaseModel):
    code = models.CharField(_('District code'), max_length=50, null=True, blank=True)
    name = models.CharField(_('District name'), max_length=255, null=True, blank=True)
    region = models.ForeignKey(Region, related_name='districts', on_delete=models.SET_NULL, null=True, blank=True)
    geo_json = models.TextField(_('GeoJson'), blank=True)
    center_x = models.FloatField(blank=True, null=True)
    center_y = models.FloatField(blank=True, null=True)
    zoom = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _('district')
        verbose_name_plural = _('districts')

    def __str__(self):
        return self.name


class Gom(BaseModel):
    code = models.CharField(_('Gom code'), max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    region = models.ForeignKey(Region, related_name='gom_region', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, related_name='gom_district', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _('Gom')
        verbose_name_plural = _('Goms')

    def __str__(self):
        return self.name


class Mahalla(BaseModel):
    code = models.CharField(_('Mahalla code'), max_length=50, null=True, blank=True)
    name = models.CharField(_('Mahalla name'), max_length=255, null=True, blank=True)
    region = models.ForeignKey(Region, related_name='mahalla_region', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, related_name='mahalla_district', on_delete=models.SET_NULL, null=True, blank=True)
    gom = models.ForeignKey(Gom, related_name='mahalla_gom', on_delete=models.SET_NULL, null=True, blank=True)
    geo_json = models.TextField(_('GeoJson'), blank=True)
    center_x = models.FloatField(blank=True, null=True)
    center_y = models.FloatField(blank=True, null=True)
    zoom = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _('Mahalla')
        verbose_name_plural = _('Mahallas')

    def __str__(self):
        return self.name




class Organization(BaseModel):
    name = models.CharField(_('Organization name'), max_length=255, null=True, blank=True,
                            help_text=_("Tashkilotning to‘liq nomini kiriting"))
    number = models.CharField(_('Number'), max_length=255, null=True, blank=True,
                              help_text=_("Tashkilotning raqamini yoki tartib raqamini kiriting"))
    code = models.CharField(_('Code'), max_length=255, null=True, blank=True,
                            help_text=_("Tashkilotning kodini kiriting (agar mavjud bo‘lsa)"))
    region = models.ForeignKey(Region, related_name='organ_region', on_delete=models.SET_NULL, null=True, blank=True,
                               help_text=_("Viloyat jadvali bilan bog'lanish"))
    district = models.ForeignKey(District, related_name='organ_district', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Tuman jadvali bilan bog'lanish"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='organ_mahalla', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        indexes = [
            models.Index(fields=['region', 'district']),
        ]

    def __str__(self):
        return self.name


class Department(BaseModel):
    name = models.CharField(_('Department name'), max_length=255, null=True, blank=True,
                            help_text=_("Bo‘limning nomini kiriting"))
    organization = models.ForeignKey(Organization, related_name='departments', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Bo‘lim tegishli tashkilotni tanlang"))

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')

    def __str__(self):
        return self.name


class Position(BaseModel):
    name = models.CharField(_('Position name'), max_length=255, null=True, blank=True,
                            help_text=_("Lavozim nomini kiriting"))
    department = models.ForeignKey(Department, related_name='positions', on_delete=models.SET_NULL, null=True,
                                   blank=True, help_text=_("Lavozim tegishli bo‘lgan bo‘limni tanlang"))

    class Meta:
        verbose_name = _('position')
        verbose_name_plural = _('positions')

    def __str__(self):
        return self.name
