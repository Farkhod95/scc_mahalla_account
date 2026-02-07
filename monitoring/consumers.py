import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("metrics_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("metrics_group", self.channel_name)

    async def metric(self, event):
        metric = event.get("metric")
        await self.send(text_data=json.dumps({
            "type": "metric",
            "metric": metric
        }))
