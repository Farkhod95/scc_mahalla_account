"""
Damafon mikroservis WebSocket PROXY consumer'lari (Channels/ASGI).

Bizning backend client (frontend) bilan damafon mikroservis WS i o'rtasida
ko'prik bo'ladi — xabarlarni ikki tomonga uzatadi:
  - /ws/damafon/           -> mikroservis /ws            (incoming_call hodisalari)
  - /ws/damafon/talkback/  -> mikroservis /ws/talkback   (mikrofon -> damafon, binary)

Mikroservis self-signed (wss) va auth ochiq.
"""
import asyncio
import json
import ssl

import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

DAMAFON_GROUP = "damafon"  # listener shu group ga incoming_call ni broadcast qiladi

_BASE = getattr(settings, "DAMAFON_BASE_URL", "https://192.168.168.170:8000").rstrip("/")
# https -> wss, http -> ws
_WS_BASE = _BASE.replace("https://", "wss://").replace("http://", "ws://")

_NO_VERIFY = ssl.create_default_context()
_NO_VERIFY.check_hostname = False
_NO_VERIFY.verify_mode = ssl.CERT_NONE


class _BaseDamafonProxy(AsyncWebsocketConsumer):
    """Client <-> mikroservis WS ko'prigi. upstream_path() ni override qiling."""

    upstream = None
    pump_task = None

    def upstream_path(self) -> str:
        return "/ws"

    async def connect(self):
        await self.accept()
        url = f"{_WS_BASE}{self.upstream_path()}"
        ssl_arg = _NO_VERIFY if url.startswith("wss://") else None
        try:
            self.upstream = await websockets.connect(url, ssl=ssl_arg, max_size=None)
        except Exception:
            await self.close()
            return
        self.pump_task = asyncio.create_task(self._pump())

    async def _pump(self):
        """Mikroservis -> client."""
        try:
            async for msg in self.upstream:
                if isinstance(msg, (bytes, bytearray)):
                    await self.send(bytes_data=bytes(msg))
                else:
                    await self.send(text_data=msg)
        except Exception:
            pass
        finally:
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        """Client -> mikroservis."""
        if self.upstream is None:
            return
        try:
            if bytes_data is not None:
                await self.upstream.send(bytes_data)
            elif text_data is not None:
                await self.upstream.send(text_data)
        except Exception:
            await self.close()

    async def disconnect(self, code):
        if self.pump_task is not None:
            self.pump_task.cancel()
        if self.upstream is not None:
            try:
                await self.upstream.close()
            except Exception:
                pass


class DamafonEventConsumer(AsyncWebsocketConsumer):
    """
    /ws/damafon/ — frontend jonli `incoming_call` ni shu yerdan oladi.

    Proxy EMAS: bitta markaziy listener (management command) mikroservis WS ni
    tinglaydi, DamafonCall ga yozadi va "damafon" group ga broadcast qiladi.
    Bu consumer faqat shu group ga obuna bo'ladi (har client mikroservisga
    alohida ulanmaydi). Frontend ko'rinishi: {"type": "incoming_call", "data": {...}}.
    """

    async def connect(self):
        await self.channel_layer.group_add(DAMAFON_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(DAMAFON_GROUP, self.channel_name)

    async def damafon_call(self, event):
        await self.send(text_data=json.dumps({"type": "incoming_call", "data": event["data"]}))


class DamafonTalkbackConsumer(_BaseDamafonProxy):
    """/ws/damafon/talkback/?damafon_id=ID -> mikroservis /ws/talkback?damafon_id=ID."""

    def upstream_path(self) -> str:
        qs = self.scope.get("query_string", b"").decode()
        return f"/ws/talkback?{qs}" if qs else "/ws/talkback"
