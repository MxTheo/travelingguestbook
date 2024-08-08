from django.forms import ModelForm, Textarea
from .models import LogMessage, Sociable


class LogMessageForm(ModelForm):
    '''The form the sociable reciever uses to leave a message on the sociable page'''
    class Meta:
        model   = LogMessage
        fields  = ['name', 'body']
        widgets = {
            'body': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Vertel iets over je ervaringen van het gesprek. Voel je vrij te delen wat je wilt delen en niet te delen wat je niet wilt delen.'})
        }


class SociableForm(ModelForm):
    '''The form for sociable'''
    class Meta:
        model   = Sociable
        fields  = ['description']
        widgets = {
            'description': Textarea(attrs={
                'rows': 5,
                'placeholder': 'Vrije ruimte en optioneel: Misschien heb je wel iets wat je wilt weten van anderen. Hier is de ruimte om verzoeken te doen aan degene die hier een berichtje achter laten'})
        }
