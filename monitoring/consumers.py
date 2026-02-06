# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
# class WSConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.channel_layer.group_add("metrics_group", self.channel_name)
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("metrics_group", self.channel_name)
#
#     async def send_metric(self, event):
#         metric = event['metric']
#
#
#         await self.send(text_data=json.dumps(metric))
#
# class WSServiceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.channel_layer.group_add("service_group", self.channel_name)
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("service_group", self.channel_name)
#
#     async def send_metric(self, event):
#         metric = event['service']
#
#
#         await self.send(text_data=json.dumps(metric))
#
# # class WSConsumer (WebsocketConsumer):
# #     def connect(self):
# #         self.accept()
# #         for i in range(1000):
# #             self.send(json.dumps({'message': randint(1, 100)}))
# #             sleep (1)