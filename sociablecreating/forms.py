from django.forms import ModelForm, Textarea, TextInput
from .models import LogMessage


class LogMessageForm(ModelForm):
    '''The form the sociable reciever uses to leave a message on the sociable page'''
    class Meta:
        model   = LogMessage
        fields  = ['name', 'body']
        widgets = {
            'name': TextInput(attrs={
                'placeholder': 'Anoniem'
            }),
            'body': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Vertel iets over je ervaringen van het contact. Voel je vrij te delen wat je wilt delen en niet te delen wat je niet wilt delen.'})
        }
