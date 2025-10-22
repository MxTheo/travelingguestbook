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

class ExperienceForm(forms.ModelForm):
    """Form for creating or updating an Experience."""

    class Meta:
        '''Model form for the Experience model.'''
        model = Experience
        fields = ['report', 'fase', 'tags']
        labels = {
            'fase': 'Fase van de ervaring',
            'tags': 'Tags voor de ervaring',
            'report': 'Beschrijving van de ervaring',
        }
        help_texts = {
            'fase': 'Selecteer de fase waarin deze ervaring plaatsvond.',
            'tags': 'Kies relevante tags voor deze ervaring.',
            'report': 'Beschrijf je ervaring in detail.',
        }
        widgets = {
            'fase': forms.Select(),
            'tags': forms.CheckboxSelectMultiple(),
            'report': forms.Textarea(attrs={'rows': 4}),
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
