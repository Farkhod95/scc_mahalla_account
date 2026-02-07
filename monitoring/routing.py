from django.urls import path
from .consumers import WSConsumer

websocket_urlpatterns = [
    path('ws/gps-url/', WSConsumer.as_asgi()),
]