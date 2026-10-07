from django import forms
from django.core.exceptions import ValidationError

from .models import Reflection, StreetActivity


class StreetActivityForm(forms.ModelForm):
    """Form for a StreetActivity."""

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

class ReflectionForm(forms.ModelForm):
    """Base form for Reflection with common fields."""

    class Meta:
        model = Reflection
        fields = ['reflection']
        widgets = {
            'reflection': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder':
                'Jouw reflectie over het contact maken op straat...'}),
        }
        labels = {
            'reflection': 'Hoe denk je terug over het doen van deze activiteit?',
        }
        help_texts = {
            'reflection': """Wat heb je geleerd? Tips, suggesties?
            Jouw ervaring draagt bij aan het begrijpen van deze activiteit!""",
        }

    def clean(self):
        """Custom validation to ensure reflection is provided."""
        cleaned_data = super().clean()
        reflection = cleaned_data.get('reflection')

        if not reflection:
            self.add_error('reflection', 'Geen reflectie gegeven')

        return cleaned_data
