from django import forms
from .models import StreetActivity, Experience, Tag

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
        fields = ['fase', 'tags', 'report', 'external_link']
        widgets = {
            'report': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder':
                'Omschrijf je innerlijke beleving...'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control'}),
            'fase': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'fase': 'Hoe zelfverzekerd voelde je je?',
            'tags': 'Welke woorden passen bij je moment?',
            'report': 'Wat voelde je? Wat ging er in je om?',
            'external_link': 'Link naar meer informatie (optioneel)',
        }
        help_texts = {
            'tags': 'Kies 3 kernwoorden om je moment te omschrijven',
            'report': 'Beschrijf wat zich aandiende in maximaal 3500 karakters',
            'external_link': 'Link naar een blog of iets anders',
        }

class TagForm(forms.ModelForm):
    """Form for creating or updating a Tag."""

    class Meta:
        '''Model form for the Tag model.'''
        model = Tag
        fields = ['name', 'nvc_category', 'maintag']
        labels = {
            'name': 'Naam van de tag',
            'nvc_category': 'Behoefte of gevoel',
            'maintag': 'Hoofdtag',
        }
        help_texts = {
            'name': 'Voer de naam van de tag in.',
            'nvc_category': 'Selecteer of dit een behoefte of gevoel is.',
            'maintag': 'Kies een hoofdtag als dit een subtag is.',
        }
