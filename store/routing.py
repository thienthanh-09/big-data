from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<role>\w+)/(?P<id>\w+)/', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/noti/', consumers.NotificationConsumer.as_asgi()),
]