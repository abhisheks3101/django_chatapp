from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import ChatGroup, GroupMessage
from asgiref.sync import async_to_sync
import json
from django.template.loader import render_to_string

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user'] # get the user from the scope, we don't have request in websocket
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        async_to_sync(self.channel_layer.group_add)(self.chatroom_name, self.channel_name)

        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()
        self.accept()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        message = GroupMessage(
            body=body,
            author=self.user,
            group=self.chatroom,
        )
        message.save()
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self, event):
        # send message to room group
        message = GroupMessage.objects.get(id=event['message_id'])
        context = {
            'chat_message': message,
            'user': self.user,
        }
        html = render_to_string('a_rtchat/partials/chat_message_p.html', context = context)
        self.send(text_data=html)


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,
            self.channel_name
        )
        # remove user from online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def update_online_count(self):
        online_count = self.chatroom.users_online.count() - 1
        event = {'type': 'online_count_handler', 'online_count': online_count}
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def online_count_handler(self, event):
        online_count = event['online_count']
        html = render_to_string('a_rtchat/partials/online_count.html', {'online_count': online_count})
        self.send(text_data=html)
