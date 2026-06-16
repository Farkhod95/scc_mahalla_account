"""
Damafon (Dahua VTO intercom) mikroservis REST client.

Bizning backend faqat PROXY qiladi — damafon ma'lumoti mikroservis (PostgreSQL)
da saqlanadi. Mahalla bog'lanishi: damafon `location_id` = directory.Mahalla.id.

Mikroservis: https://<host>:8000 (self-signed -> verify=False), auth yo'q (ochiq).
"""
import requests
import urllib3
from django.conf import settings

BASE_URL = getattr(settings, "DAMAFON_BASE_URL", "https://192.168.168.170:8000").rstrip("/")
VERIFY_SSL = getattr(settings, "DAMAFON_VERIFY_SSL", False)
TIMEOUT = getattr(settings, "DAMAFON_TIMEOUT", 15)

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def list_damafons():
    r = requests.get(_url("/api/damafons"), timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.json()


def get_damafon(damafon_id):
    r = requests.get(_url(f"/api/damafons/{damafon_id}"), timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.json()


def create_damafon(payload: dict):
    r = requests.post(_url("/api/damafons"), json=payload, timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.json()


def update_damafon(damafon_id, payload: dict):
    r = requests.put(_url(f"/api/damafons/{damafon_id}"), json=payload, timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.json()


def delete_damafon(damafon_id):
    r = requests.delete(_url(f"/api/damafons/{damafon_id}"), timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.status_code


def snapshot(damafon_id):
    """(bytes, content_type) — damafondan oxirgi rasm (JPEG)."""
    r = requests.get(_url(f"/api/damafons/{damafon_id}/snapshot"), timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.content, r.headers.get("Content-Type", "image/jpeg")


def webrtc(damafon_id, sdp_offer: str) -> str:
    """WebRTC SDP: brauzer offer (text/plain) -> mikroservis go2rtc -> SDP answer."""
    r = requests.post(
        _url("/api/webrtc"),
        params={"damafon_id": damafon_id},
        data=sdp_offer.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        timeout=TIMEOUT,
        verify=VERIFY_SSL,
    )
    r.raise_for_status()
    return r.text


def doorbell(payload: dict):
    r = requests.post(_url("/api/doorbell"), json=payload or {}, timeout=TIMEOUT, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.json() if r.content else {}
