from django.forms import ModelForm, Textarea
from .models import LogMessage, Sociable

class LogMessageForm(ModelForm):
    class Meta:
        model   = LogMessage
        fields  = ['name', 'body']
        widgets = {
            'body': Textarea(attrs={'rows':3})
        }

class SociableForm(ModelForm):
    class Meta:
        model   = Sociable
        fields  = ['goal', 'description']
        widgets = {
            'description': Textarea(attrs={'rows':5})
        }