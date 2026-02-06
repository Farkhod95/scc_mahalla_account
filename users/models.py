from directory.models import Organization, Department, Position
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, GroupManager
from django.utils.translation import gettext_lazy as _

GENDERS = (
    ('male', _('Male')),
    ('female', _('Female')),
)

TYPE = (
    ('individual', _('Individual')),
    ('legal_entity', _('Legal entity')),
)

class CommonInfo(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_time = models.DateTimeField(auto_now_add=False, auto_now=True)


class Role(Group):
    objects = GroupManager()
    type = models.CharField(choices=TYPE, max_length=20, null=True, blank=True, )
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, help_text=_("Foydalanuvchi nomi"))
    last_name = models.CharField(max_length=100, help_text=_("Foydalanuvchi familiyasi"))
    first_name = models.CharField(max_length=100, help_text=_("Foydalanuvchi ismi"))
    second_name = models.CharField(max_length=100, null=True, blank=True, help_text=_("Foydalanuvchi otasining ismi"))
    is_active = models.BooleanField(_('Active'), default=True, help_text=_("Foydalanuvchi holati"))
    date_of_birthday = models.DateField(_('date of birthday'), null=True, blank=True, help_text=_("Tug‘ilgan sanasi"))
    gender = models.CharField(choices=GENDERS, max_length=6, null=True, blank=True, )
    phone_number = models.CharField(_("Phone number"), max_length=100, help_text=_("Telefon raqami"))
    email = models.EmailField(_('email address'), blank=True, null=True, help_text=_("Email manzili"))
    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True, help_text=_("Ro‘yxatdan o‘tgan sana"))
    password = models.CharField(max_length=255, null=True, blank=True, help_text=_("Parol"))
    organization = models.ForeignKey(Organization, related_name='user_department', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Tashkilot"))
    department = models.ForeignKey(Department, related_name='user_department', on_delete=models.SET_NULL, null=True,
                                   blank=True, help_text=_("Bo‘lim"))
    position = models.ForeignKey(Position, related_name='user_position', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Lavozim"))
    region = models.ForeignKey("directory.Region", related_name='user_region', on_delete=models.SET_NULL, null=True,
                               blank=True,
                               help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='user_district', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    role = models.ForeignKey(Role, related_name='role_user', null=True, on_delete=models.SET_NULL)
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null=True, blank=True, help_text=_("Profil rasmi"))
    pinfl = models.CharField(_('JSHSHIR'), max_length=14, unique=True, null=True, blank=True,
                             help_text=_("Jismoniy shaxsning shaxsiy identifikatsion raqami"))
    passport_series = models.CharField(_('passport series'), max_length=10, blank=True, help_text=_("Pasport seriyasi"))
    passport_number = models.CharField(_('Full name'), max_length=20, blank=True, help_text=_("Pasport raqami"))

    created_time = models.DateTimeField(auto_now_add=True, help_text=_("Yaratilgan vaqt"))
    updated_time = models.DateTimeField(auto_now=True, help_text=_("Yangilangan vaqt"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_by_user', null=True,
                                   on_delete=models.SET_NULL, help_text=_("Yaratgan foydalanuvchi"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='updated_by_user', null=True,
                                   on_delete=models.SET_NULL, help_text=_("Yangilagan foydalanuvchi"))
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f'{self.first_name} {self.last_name}' if (self.first_name or self.last_name) else self.username

    def is_admin(self) -> bool:
        return bool(self.role_id) and self.role.name == 'Super Admin'



class AppModule(models.Model):
    name = models.CharField(_('Module name'), max_length=125, blank=True)
    on_dashboard = models.BooleanField(default=False)
    content_types = models.ManyToManyField(ContentType)
    sorting = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
