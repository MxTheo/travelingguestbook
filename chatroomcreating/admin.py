from django.contrib import admin
from .models import ChatRoom, ChatMessage

admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
