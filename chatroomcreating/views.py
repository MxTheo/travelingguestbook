import base64
import os
from django.shortcuts import redirect, render
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from chatroomcreating.forms import ChatMessageForm
from .models import ChatMessage, ChatRoom


def home(request):
    """Renders the homepage of the chatroomcreating app"""
    return render(request, "chatroomcreating/index.html")

def create_chatroom(request):
    """Creates a chatroom and redirects to it's detail page"""
    slug = get_random_string(9, allowed_chars='abcdefghjklmnpqrstuvwxyz23456789')
    key = os.urandom(32)
    key = base64.b64encode(key).decode()
    chatroom = ChatRoom(slug=slug, secret_key=key)
    chatroom.save()
    return redirect(reverse("chatroom", args=[chatroom.slug]))

class ChatMessageCreate(generic.edit.CreateView):
    """Generic editing view to create ChatMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    form_class = ChatMessageForm
    model = ChatMessage

    def dispatch(self, request, *args, **kwargs):
        '''Override dispatch to get the chatroom from the URL slug. And save at self.chatroom'''
        self.chatroom = ChatRoom.objects.get(slug=self.kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chatroom"] = self.chatroom
        return context


    def form_valid(self, form):
        '''Link the chatroom to the message'''
        form.instance.chatroom = self.chatroom
        return super().form_valid(form)

class ChatMessageDelete(generic.edit.DeleteView):
    """Generic editing view to delete ChatMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = ChatMessage
    template_name = "admin/confirm_delete.html"

    def get_success_url(self):
        chatmessage = self.get_object()
        chatroom = chatmessage.chatroom
        return reverse("chatroom", kwargs={"slug": chatroom.slug})


class ChatRoomDelete(generic.edit.DeleteView):
    """Generic editing view to delete ChatRoom:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = ChatRoom
    success_url = reverse_lazy("chat")
    template_name = "admin/confirm_delete.html"


class ChatRoomDetail(generic.DetailView):
    """Generic display view to show detailpage of ChatRoom:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model = ChatRoom

class ChatRoomList(generic.ListView):
    """Generic display view to show an overview of ChatRoom:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model = ChatRoom
