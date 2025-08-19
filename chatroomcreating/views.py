from django.utils import timezone
from django.forms import BaseModelForm
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
    slug = get_random_string(21, allowed_chars='abcdefghjklmnpqrstuvwxyz23456789')
    chatroom = ChatRoom(slug=slug)
    chatroom.save()
    return redirect(reverse("chatroom", args=[chatroom.slug]))

class ChatMessageCreate(generic.edit.CreateView):
    """Generic editing view to create ChatMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    form_class = ChatMessageForm
    model = ChatMessage

    def get_initial(self):
        """If logged in, the username is entered as initial value of name"""
        initial = super().get_initial()
        user = self.request.user
        if not user.is_anonymous:
            initial["name"] = user.username
        return initial

    def form_valid(self, form):
        """After the form is valid, set the relationships"""
        self.set_chatroom(form)
        return super(ChatMessageCreate, self).form_valid(form)

    def set_chatroom(self, form):
        """Given the chatmessage and the chatroom slug from the context,
        sets the chatroom relationship for the created chatmessage"""
        slug = super().get_context_data()["view"].kwargs["slug"]
        chatroom = ChatRoom.objects.get(slug=slug)
        form.instance.chatroom = chatroom

class ChatMessageDelete(generic.edit.DeleteView):
    """Generic editing view to delete ChatMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = ChatMessage
    template_name = "admin/confirm_delete.html"

    def get_success_url(self):
        chatmessage = self.get_object()
        chatroom = chatmessage.chatroom
        return reverse("chatroom", kwargs={"slug": chatroom.slug})


class ChatMessageUpdate(generic.edit.UpdateView):
    """Generic editing view to update ChatMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = ChatMessage
    form_class = ChatMessageForm

    def form_valid(self, form: BaseModelForm):
        """Set the date changed to today"""
        form.instance.date_changed = timezone.now()
        return super(ChatMessageUpdate, self).form_valid(form)

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
