"""
Barcha ShopCamera larni go2rtc ga sinxronlaydi.

Ishlatish:
    python manage.py sync_cameras_go2rtc
    python manage.py sync_cameras_go2rtc --clean   # avval barchasini o'chiradi
"""
from django.core.management.base import BaseCommand

from monitoring.models import ShopCamera
from monitoring.services import go2rtc_service


class Command(BaseCommand):
    help = "Barcha ShopCamera larni go2rtc ga ro'yxatdan o'tkazadi."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean", action="store_true",
            help="Avval go2rtc dagi barcha shop_camera_* streamlarni o'chiradi",
        )

    def handle(self, *args, **options):
        cameras = ShopCamera.objects.exclude(url__isnull=True).exclude(url__exact="")
        total = cameras.count()
        self.stdout.write(f"Jami {total} ta kamera topildi.\n")

        if options["clean"]:
            self.stdout.write("go2rtc dan eski streamlar o'chirilmoqda...")
            removed = 0
            for cam in cameras:
                if go2rtc_service.unregister_stream(cam):
                    removed += 1
            self.stdout.write(f"  {removed} ta o'chirildi.\n")

        ok = fail = 0
        for cam in cameras:
            success = go2rtc_service.register_stream(cam)
            status_label = self.style.SUCCESS("OK") if success else self.style.WARNING("FAIL")
            self.stdout.write(
                f"  [{status_label}] {go2rtc_service.stream_name(cam):25s} | {cam.url}"
            )
            if success:
                ok += 1
            else:
                fail += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nSinxronlash yakunlandi: {ok} OK, {fail} muvaffaqiyatsiz."
        ))
