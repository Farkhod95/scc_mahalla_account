"""
Damafon mikroservis WS (/ws) ni tinglaydi va har `incoming_call` ni
DamafonCall (bizning DB) ga yozadi — qo'ng'iroqlar TARIXI.

JONLI oqim (frontend) endi shu listener orqali EMAS: har client
DamafonEventConsumer (/ws/damafon/) orqali mikroservis /ws iga to'g'ridan-to'g'ri
shaffof ko'prik bilan ulanadi. Bu listener faqat tarix uchun.

Markaziy, doimiy ishlaydigan jarayon (supervisor/systemd bilan). Uzilsa 5s dan
keyin qayta ulanadi.

    python manage.py damafon_listener
"""
import asyncio
import json
import logging
import ssl

import websockets
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand

from monitoring.services import damafon_service

logger = logging.getLogger(__name__)

_BASE = getattr(settings, "DAMAFON_BASE_URL", "https://192.168.168.170:8000").rstrip("/")
_WS_URL = _BASE.replace("https://", "wss://").replace("http://", "ws://") + "/ws"

_NO_VERIFY = ssl.create_default_context()
_NO_VERIFY.check_hostname = False
_NO_VERIFY.verify_mode = ssl.CERT_NONE


@database_sync_to_async
def _store_call(msg, location_id):
    from monitoring.models import DamafonCall
    DamafonCall.objects.create(
        remote_damafon_id=msg.get("damafon_id"),
        damafon_name=msg.get("damafon_name") or "",
        host=msg.get("host") or "",
        call_id=msg.get("call_id") or "",
        stream=msg.get("stream") or "",
        location_id=location_id,
    )


async def _resolve_location_id(damafon_id):
    """Damafon location_id (=mahalla) ni mikroservisdan oladi (incoming_call da yo'q)."""
    if not damafon_id:
        return None
    try:
        device = await asyncio.to_thread(damafon_service.get_damafon, damafon_id)
        return (device or {}).get("location_id")
    except Exception:
        return None


class Command(BaseCommand):
    help = "Damafon mikroservis WS ni tinglaydi: incoming_call -> DamafonCall (tarix)."

    def handle(self, *args, **opts):
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            self.stdout.write("Damafon listener to'xtatildi.")

    async def _run(self):
        ssl_arg = _NO_VERIFY if _WS_URL.startswith("wss://") else None
        while True:
            try:
                self.stdout.write(f"Damafon WS ga ulanmoqda: {_WS_URL}")
                async with websockets.connect(_WS_URL, ssl=ssl_arg, max_size=None) as ws:
                    self.stdout.write("Ulandi. incoming_call kutilmoqda...")
                    async for raw in ws:
                        await self._on_message(raw)
            except Exception as e:
                logger.warning("damafon listener uzildi: %s", e)
                await asyncio.sleep(5)  # qayta ulanish

    async def _on_message(self, raw):
        try:
            msg = json.loads(raw)
        except (ValueError, TypeError):
            return
        if not isinstance(msg, dict) or msg.get("type") != "incoming_call":
            return
        location_id = await _resolve_location_id(msg.get("damafon_id"))
        await _store_call(msg, location_id)
