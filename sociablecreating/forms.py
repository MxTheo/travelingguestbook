from django.forms import ModelForm, Textarea
from .models import LogMessage, Sociable


class LogMessageForm(ModelForm):
    '''The form the sociable reciever uses to leave a message on the sociable page'''
    class Meta:
        model   = LogMessage
        fields  = ['name', 'body']
        widgets = {
            'body': Textarea(attrs={'rows':3})
        }


class SociableForm(ModelForm):
    '''The form for sociable'''
    class Meta:
        model   = Sociable
        fields  = ['goal', 'description']
        widgets = {
            'description': Textarea(attrs={'rows':5})
        }
