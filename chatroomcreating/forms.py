from django.forms import HiddenInput, ModelForm, Textarea, TextInput
from .models import ChatMessage


class ChatMessageForm(ModelForm):
    """The form the chatroom reciever uses to leave a message on the chatroom page"""

    class Meta:
        """Fields present on the form and extra that needs to be shown on the page"""
        model   = ChatMessage
        fields  = ["body", "nonce"]
        widgets = {
            "body": Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Schrijf hier je bericht",
                }
            ),
            "nonce": HiddenInput(),
        }
