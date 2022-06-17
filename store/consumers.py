import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils.timezone import now
from .models import Store

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        self.room_name = str(user.id)
        print(user.username + ' has been connected to notification')
        # Join room
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()
    
    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )
    
    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=json.dumps(text_data))
        return super().receive(text_data, bytes_data)