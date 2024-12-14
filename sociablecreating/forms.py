from django.forms import ModelForm, Textarea, TextInput
from .models import LogMessage


class LogMessageForm(ModelForm):
    """The form the sociable reciever uses to leave a message on the sociable page"""

    class Meta:
        """Fields present on the form and extra that needs to be shown on the page"""
        model   = LogMessage
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
