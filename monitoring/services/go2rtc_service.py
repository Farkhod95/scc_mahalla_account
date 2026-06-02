"""
go2rtc integration — ShopCamera uchun.

go2rtc stream on demand:
  - Frontend URL ni ochsa → go2rtc kameraga ulanadi
  - Frontend URL ni yopsa → go2rtc kameradan uziladi

go2rtc REST API: http://mahalla_go2rtc:1984
"""
import requests
from django.conf import settings

GO2RTC_URL         = getattr(settings, "GO2RTC_URL",         "http://mahalla_go2rtc:1984")
GO2RTC_PUBLIC_HOST = getattr(settings, "GO2RTC_PUBLIC_HOST", "localhost")
GO2RTC_STREAM_BASE = getattr(settings, "GO2RTC_STREAM_BASE", f"http://{GO2RTC_PUBLIC_HOST}:1984")
TIMEOUT = 5


def stream_name(camera) -> str:
    return f"shop_camera_{camera.pk}"


def get_webrtc_url(camera) -> str | None:
    """Frontend WebRTC stream URL si. None — agar kamerada URL yo'q bo'lsa."""
    if not camera.url:
        return None
    return f"{GO2RTC_STREAM_BASE}/api/ws?src={stream_name(camera)}"


def register_stream(camera) -> bool:
    """Kamerani go2rtc ga qo'shadi. ShopCamera saqlanganida chaqiriladi."""
    if not camera.url:
        return False
    try:
        r = requests.put(
            f"{GO2RTC_URL}/api/streams",
            params={"name": stream_name(camera), "src": camera.url},
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except requests.RequestException:
        return False


def unregister_stream(camera) -> bool:
    """Kamerani go2rtc dan o'chiradi. ShopCamera o'chirilganida chaqiriladi."""
    try:
        r = requests.delete(
            f"{GO2RTC_URL}/api/streams",
            params={"name": stream_name(camera)},
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except requests.RequestException:
        return False


def sync_all() -> int:
    """Barcha mavjud kameralarni go2rtc ga ro'yxatdan o'tkazadi. Startup da ishlatiladi."""
    from monitoring.models import ShopCamera
    count = 0
    for cam in ShopCamera.objects.exclude(url__isnull=True).exclude(url__exact=""):
        if register_stream(cam):
            count += 1
    return count
