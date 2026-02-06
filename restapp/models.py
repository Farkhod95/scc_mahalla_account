from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType

from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class BaseModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_time = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_%(model_name)s', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, related_name='updated_%(model_name)s', null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        ordering = ('id',)
        get_latest_by = 'created_time'


class TranslationTerm(BaseModel):
    term_name = models.CharField(_('Term name'), max_length=500, blank=False, null=True)
    name = models.CharField(_('Name'), max_length=500, blank=False, null=False)


class ModelAudit(models.Model):
    user = models.ForeignKey(User, related_name='audit_user', null=True, on_delete=models.SET_NULL)
    module = models.CharField(max_length=255, null=False, blank=True)
    instance = models.CharField(max_length=255, null=False, blank=True)
    instance_id = models.BigIntegerField(null=True, blank=True)
    field_name = models.TextField(null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=16, null=False, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)



class ExtendedContentType(models.Model):
    extend_name = models.CharField(_('Extended name'), max_length=100, null=True, blank=True)
    content_type = models.OneToOneField(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=False, null=True, blank=True)

    def __str__(self):
        return self.extend_name
