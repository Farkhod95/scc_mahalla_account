from directory.models import Organization, Department, Position
from django.db import models
from django.utils.translation import gettext_lazy as _

from restapp.models import BaseModel

GENDERS = (
    ('male', _('Male')),
    ('female', _('Female')),
)

class Employee(BaseModel):
    full_name = models.CharField(max_length=255, help_text=_("Hodim fio"))
    date_of_birthday = models.DateField(_('date of birthday'), null=True, blank=True, help_text=_("Tug‘ilgan sanasi"))
    gender = models.CharField(choices=GENDERS, max_length=6, null=True, blank=True, )
    phone_number = models.CharField(_("Phone number"), max_length=100, help_text=_("Telefon raqami"))
    organization = models.ForeignKey(Organization, related_name='employees', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Tashkilot"))
    department = models.ForeignKey(Department, related_name='employees', on_delete=models.SET_NULL, null=True,
                                   blank=True, help_text=_("Bo‘lim"))
    date_of_appointment = models.DateField(_('Date of appointment'), null=True, blank=True, help_text=_("Tug‘ilgan sanasi"))
    position = models.ForeignKey(Position, related_name='employees', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Lavozim"))
    region = models.ForeignKey("directory.Region", related_name='employees', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='employees', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='employees', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Mahalla"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    avatar = models.ImageField(upload_to='employee/%Y/%m/%d', null=True, blank=True, help_text=_("Profil rasmi"))

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    def __str__(self):
        return self.full_name if self.full_name else self.id


class MahallaInformation(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    count = models.IntegerField(default=0, null=True, blank=True, help_text=_("Soni"))
    icon = models.TextField(null=True, blank=True, help_text=_("SVG icon"))

    class Meta:
        verbose_name = _('Mahalla Information')
        verbose_name_plural = _('Mahalla Informations')

    def __str__(self):
        return self.name if self.name else self.count


class ObjectCategory(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))

    class Meta:
        verbose_name = _('Object Category')
        verbose_name_plural = _('Object Categories')

    def __str__(self):
        return self.name if self.name else self.id


class Object(BaseModel):
    category = models.ForeignKey(ObjectCategory, related_name='category_objects', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Kategoriya"))
    organization = models.ForeignKey("directory.Organization", related_name='objects', on_delete=models.SET_NULL,
                                     null=True, blank=True, help_text=_("Tashkilot"))
    full_name = models.CharField(max_length=255, help_text=_("Rahbar fio"))
    avatar = models.ImageField(upload_to='object_employee/%Y/%m/%d', null=True, blank=True, help_text=_("Profil rasmi"))
    phone_number = models.CharField(_("Phone number"), max_length=100, help_text=_("Telefon raqami"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))

    class Meta:
        verbose_name = _('Object')
        verbose_name_plural = _('Objects')

    def __str__(self):
        return self.organization.name if self.organization else str(self.id)


# Jinoyat kategoriyasi
class CrimeCategory(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))

    class Meta:
        verbose_name = _('Crime Category')
        verbose_name_plural = _('Crime Categories')

    def __str__(self):
        return self.name if self.name else self.id


# Mahallada sodir etilgan jonoyatchilik
class MahallaCrime(BaseModel):
    category = models.ForeignKey(ObjectCategory, related_name='crimes', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Jinoyat kategoriyasi"))
    date = models.DateField(_('Date'), null=True, blank=True, help_text=_("Jinoyat sodir etilgan sana"))
    article = models.CharField(max_length=255, help_text=_("Modda"))
    description = models.TextField(_("Description"), null=True, blank=True, help_text=_("Tasnif"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))

    class Meta:
        verbose_name = _('Mahalla Crime')
        verbose_name_plural = _('Mahalla Crimes')

    def __str__(self):
        return self.article if self.article else self.id


# Patrolga biriktirilgan Avtomobillar
class PatrolCar(BaseModel):
    model = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    license_plate = models.CharField(max_length=255, null=True, blank=True, help_text=_("Avtomobil raqami"))
    gps_number = models.CharField(max_length=255, null=True, blank=True, help_text=_("GPS raqami"))

    class Meta:
        verbose_name = _('Patrol Car')
        verbose_name_plural = _('Patrol Cars')

    def __str__(self):
        return self.license_plate if self.license_plate else self.model


# Kamera malumtlari
class CameraInformation(BaseModel):
    class STATUS(models.TextChoices):
        INSTALLED = 'Installed', _('Installed')
        PLANNED = 'Planned', _('Planned')
    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    direction = models.CharField(max_length=255, null=True, blank=True, help_text=_("Yo'nalish"))
    status = models.CharField(max_length=30, choices=STATUS.choices,
                            verbose_name=_('Camera status'), help_text=_("Kamera holati"))
    ip_address = models.CharField(max_length=255, null=True, blank=True, help_text=_("Ip address"))
    region = models.ForeignKey("directory.Region", related_name='cameras', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='cameras', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    login = models.CharField(max_length=100, null=True, blank=True, help_text=_("Login"))
    parol = models.CharField(max_length=100, null=True, blank=True, help_text=_("parol"))
    camera_type = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kamer turi"))

    class Meta:
        verbose_name = _('Camera Information')
        verbose_name_plural = _('Camera Informations')

    def __str__(self):
        return self.ip_address if self.ip_address else self.object_name


