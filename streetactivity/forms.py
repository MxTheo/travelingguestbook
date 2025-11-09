from django import forms
from .models import StreetActivity, Experience

class StreetActivityForm(forms.ModelForm):
    """Form for creating or updating a StreetActivity."""

    class Meta:
        '''Model form for the StreetActivity model.'''
        model = StreetActivity
        fields = ['name', 'description', 'method', 'question', 'supplies']
        labels = {
            'name': 'Naam van de activiteit',
            'description': 'Stap-voor-stap handleiding',
            'method': 'Methode van benadering',
            'question': 'Kernvraag',
            'supplies': 'Benodigdheden voor de activiteit'
        }
        help_texts = {
            'name': 'Vul alsjeblieft de naam van de activiteit in.',
            'description': 'Geef een stap-voor-stap uitleg hoe je de activiteit uitvoert.',
            'method': 'Kies hoe je mensen benadert: uitnodigen of aanspreken.',
            'question': 'Formuleer de kernvraag die je gebruikt om mensen uit te nodigen of aan te spreken.',
            'supplies': 'Welke materialen heb je nodig voor deze activiteit?',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'supplies': forms.Textarea(attrs={'rows': 3}),
        }

# forms.py
class ExperienceForm(forms.ModelForm):
    """Base form for Experience with common fields."""

    class Meta:
        model = Experience
        fields = ['fase', 'report', 'keywords']
        widgets = {
            'report': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder':
                'Omschrijf je innerlijke beleving...'}),
            'fase': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'keywords': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
                'placeholder':
                "Energiek, ongeduldig, vertrouwen..."}),
        }
        labels = {
            'fase': 'Hoe zelfverzekerd voelde je je?',
            'report': 'Wat voelde je? Wat ging er in je om?',
            'keywords': "3 woorden die je moment samenvatten, gescheiden door komma's",
        }
        help_texts = {
            'report': 'Beschrijf wat zich aandiende in maximaal 3500 karakters',
            'keywords': 'Voorbeelden: Energiek, ongeduldig, kalm, vertrouwen'
        }
