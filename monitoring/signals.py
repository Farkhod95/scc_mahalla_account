from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from monitoring.models import ShopCamera
from monitoring.services import go2rtc_service


@receiver(post_save, sender=ShopCamera)
def on_shop_camera_save(sender, instance, **kwargs):
    if instance.url:
        go2rtc_service.register_stream(instance)
    else:
        go2rtc_service.unregister_stream(instance)


@receiver(post_delete, sender=ShopCamera)
def on_shop_camera_delete(sender, instance, **kwargs):
    go2rtc_service.unregister_stream(instance)
