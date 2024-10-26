from django.db import models
from .base_models import BaseModel
from django.contrib.auth.models import User


class ChatGroup(BaseModel):
    group_name = models.CharField(max_length=255, unique=True)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)

    def __str__(self):
        return self.group_name


class GroupMessage(BaseModel):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='chat_messages')
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')

    def __str__(self):
        return f'{self.author.username} : {self.body}'
    
    class Meta:
        ordering = ['-created_at']
