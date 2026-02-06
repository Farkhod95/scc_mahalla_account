from datetime import datetime

from django.apps import apps
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.forms import model_to_dict

from restapp.utils.request_helper import get_user
from restapp.models import ModelAudit


def save_audit(**kwargs):
    model_audit = ModelAudit()
    model_audit.module = kwargs['module']
    model_audit.instance = kwargs['instance']
    model_audit.action = kwargs['action']
    model_audit.user = kwargs['user']
    model_audit.instance_id = kwargs['instance_id']
    model_audit.timestamp = datetime.now
    model_audit.data = kwargs['data']
    model_audit.field_name = kwargs['field_name']
    model_audit.old_value = kwargs['old_value']
    model_audit.new_value = kwargs['new_value']
    model_audit.save()


def get_auditable_models():
    auditable_apps = ['users',]
    auditable_models = []
    for app in auditable_apps:
        for model in apps.get_app_config(app).get_models():
            auditable_models.append(model)
    return auditable_models


@receiver(pre_save)
def audit_log(sender, instance, **kwargs):
    if sender not in get_auditable_models():
        return

    module_name = instance._meta.db_table.split('_')[0]
    instance_name = instance._meta.db_table.split('_')[1]
    if instance.id is None:
        action = 'CREATE'
        data = model_to_dict(instance, fields=[field.name for field in instance._meta.fields])
        # print("data:", type(data['created_by']))
        save_audit(
            module=module_name,
            instance=instance_name,
            instance_id=instance.id,
            action=action,
            user=get_user(),
            # user=int(data['created_by']),
            field_name=None,
            old_value=None,
            new_value=None,
            data=None
        )
    else:
        action = 'UPDATE'
        old_instance = sender.objects.get(id=instance.id)
        old_data = model_to_dict(old_instance, fields=[field.name for field in instance._meta.fields])
        new_data = model_to_dict(instance, fields=[field.name for field in instance._meta.fields])
        # print("Data1:", old_data)
        # print("Data1:", new_data)
        for key in old_data:
            if old_data[key] != new_data[key]:
                # data = model_to_dict(instance, fields=[field.name for field in instance._meta.fields])
                save_audit(
                    module=module_name,
                    instance=instance_name,
                    instance_id=instance.id,
                    action=action,
                    user=get_user(),
                    field_name=key,
                    old_value=old_data[key],
                    new_value=new_data[key],
                    data=None
                )


@receiver(pre_delete)
def audit_delete_log(sender, instance, **kwargs):

    if sender not in get_auditable_models():
        return

    module_name = instance._meta.db_table.split('_')[0]
    instance_name = instance._meta.db_table.split('_')[1]

    save_audit(
        module=module_name,
        instance=instance_name,
        instance_id=instance.id,
        action='DELETE',
        user=get_user(),
        field_name=None,
        old_value=None,
        new_value=None,
        data=None
    )
