"""
Damafon mikroservis WS (/ws) ni tinglaydi va `incoming_call` ni:
  1) DamafonCall (bizning DB) ga yozadi — TARIX;
  2) frontend WS group ("damafon") ga broadcast qiladi — JONLI.

Markaziy, doimiy ishlaydigan jarayon (supervisor/systemd bilan). Har client emas,
faqat shu bitta listener mikroservisga ulanadi. Uzilsa 5s dan keyin qayta ulanadi.

    python manage.py damafon_listener
"""
import asyncio
import json
import logging
import ssl

import websockets
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
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
    from monitoring.serializer.damafon import DamafonCallSerializer
    obj = DamafonCall.objects.create(
        remote_damafon_id=msg.get("damafon_id"),
        damafon_name=msg.get("damafon_name") or "",
        host=msg.get("host") or "",
        call_id=msg.get("call_id") or "",
        stream=msg.get("stream") or "",
        location_id=location_id,
    )
    return dict(DamafonCallSerializer(obj).data)


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
    help = "Damafon mikroservis WS ni tinglaydi: incoming_call -> DB + frontend broadcast."

    def handle(self, *args, **opts):
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            self.stdout.write("Damafon listener to'xtatildi.")

    async def _run(self):
        layer = get_channel_layer()
        ssl_arg = _NO_VERIFY if _WS_URL.startswith("wss://") else None
        while True:
            try:
                self.stdout.write(f"Damafon WS ga ulanmoqda: {_WS_URL}")
                async with websockets.connect(_WS_URL, ssl=ssl_arg, max_size=None) as ws:
                    self.stdout.write("Ulandi. incoming_call kutilmoqda...")
                    async for raw in ws:
                        await self._on_message(raw, layer)
            except Exception as e:
                logger.warning("damafon listener uzildi: %s", e)
                await asyncio.sleep(5)  # qayta ulanish

    async def _on_message(self, raw, layer):
        try:
            msg = json.loads(raw)
        except (ValueError, TypeError):
            return
        if not isinstance(msg, dict) or msg.get("type") != "incoming_call":
            return
        location_id = await _resolve_location_id(msg.get("damafon_id"))
        data = await _store_call(msg, location_id)
        await layer.group_send("damafon", {"type": "damafon.call", "data": data})
