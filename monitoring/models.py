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
        return self.full_name if self.full_name else str(self.id)


class MahallaInformationCategory(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    icon = models.TextField(null=True, blank=True, help_text=_("SVG icon"))

    class Meta:
        verbose_name = _('Mahalla Information Category')
        verbose_name_plural = _('Mahalla Information Categories')

    def __str__(self):
        return self.name if self.name else str(self.id)


class MahallaInformation(BaseModel):
    count = models.IntegerField(default=0, null=True, blank=True, help_text=_("Soni"))
    category = models.ForeignKey(MahallaInformationCategory, related_name='mahalla_informations', on_delete=models.SET_NULL,
                               null=True,
                               blank=True, help_text=_("Viloyat"))
    region = models.ForeignKey("directory.Region", related_name='mahalla_informations', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='mahalla_informations', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='mahalla_informations', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

    class Meta:
        verbose_name = _('Mahalla Information')
        verbose_name_plural = _('Mahalla Informations')

    def __str__(self):
        return str(self.count) if self.count is not None else str(self.id)


class ObjectCategory(BaseModel):
    key = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    icon = models.TextField(null=True, blank=True, help_text=_("SVG icon"))

    class Meta:
        verbose_name = _('Object Category')
        verbose_name_plural = _('Object Categories')

    def __str__(self):
        return self.name if self.name else str(self.id)


class Object(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True, help_text=_("Nomi"))
    category = models.ForeignKey(ObjectCategory, related_name='category_objects', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Kategoriya"))
    organization = models.ForeignKey("directory.Organization", related_name='organization_objects', on_delete=models.SET_NULL,
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
        return self.name if self.name else str(self.id)


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
    category = models.ForeignKey(CrimeCategory, related_name='crimes', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Jinoyat kategoriyasi"))
    date = models.DateField(_('Date'), null=True, blank=True, help_text=_("Jinoyat sodir etilgan sana"))
    article = models.CharField(max_length=255, help_text=_("Modda"))
    description = models.TextField(_("Description"), null=True, blank=True, help_text=_("Tasnif"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    region = models.ForeignKey("directory.Region", related_name='mahalla_crimes', on_delete=models.SET_NULL,
                               null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='mahalla_crimes', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='mahalla_crimes', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

    class Meta:
        verbose_name = _('Mahalla Crime')
        verbose_name_plural = _('Mahalla Crimes')

    def __str__(self):
        return self.article if self.article else str(self.id)


# Patrolga biriktirilgan Avtomobillar
class PatrolCar(BaseModel):
    mobjectId = models.IntegerField(null=True, blank=True, help_text=_("Mobile ID"))
    mobject_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    plate_number = models.CharField(max_length=255, null=True, blank=True, help_text=_("plate number"))
    imei = models.CharField(max_length=255, null=True, blank=True, help_text=_("imei"))
    brand_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("brand Name"))
    group_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("group Name"))
    last_date = models.DateField(null=True, blank=True, help_text=_("Last date"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))


    class Meta:
        verbose_name = _('Patrol Car')
        verbose_name_plural = _('Patrol Cars')
        indexes = [
            models.Index(fields=["mobjectId"]),
        ]

    def __str__(self):
        return self.plate_number if self.plate_number else self.mobjectId


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


# Ofis Kamera malumtlari
class OfficeCamera(BaseModel):
    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    direction = models.CharField(max_length=255, null=True, blank=True, help_text=_("Yo'nalish"))
    ip_address = models.CharField(max_length=255, null=True, blank=True, help_text=_("Ip address"))
    region = models.ForeignKey("directory.Region", related_name='office_cameras', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='office_cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='office_cameras', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    login = models.CharField(max_length=100, null=True, blank=True, help_text=_("Login"))
    parol = models.CharField(max_length=100, null=True, blank=True, help_text=_("parol"))
    camera_type = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kamer turi"))

    class Meta:
        verbose_name = _('Office Camera')
        verbose_name_plural = _('Office Camera')

    def __str__(self):
        return self.ip_address if self.ip_address else self.object_name


