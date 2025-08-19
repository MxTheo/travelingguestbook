from django.forms import ModelForm, Textarea, TextInput
from .models import ChatMessage


class ChatMessageForm(ModelForm):
    """The form the chatroom reciever uses to leave a message on the chatroom page"""

    class Meta:
        """Fields present on the form and extra that needs to be shown on the page"""
        model   = ChatMessage
        fields  = ["name", "body"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Anoniem"}),
            "body": Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Schrijf over je ervaringen. Alleen hallo wordt ook gewaardeerd",
                }
            ),
        }
