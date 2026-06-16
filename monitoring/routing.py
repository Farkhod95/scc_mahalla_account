from django.urls import path
from .consumers import WSConsumer
from .damafon_consumers import DamafonEventConsumer, DamafonTalkbackConsumer

websocket_urlpatterns = [
    path('ws/gps-url/', WSConsumer.as_asgi()),
    path('ws/damafon/', DamafonEventConsumer.as_asgi()),
    path('ws/damafon/talkback/', DamafonTalkbackConsumer.as_asgi()),
]