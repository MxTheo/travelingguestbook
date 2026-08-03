from django import forms

from .models import Reflection, StreetActivity


class StreetActivityForm(forms.ModelForm):
    """Form for a StreetActivity."""

    class Meta:
        '''Model form for the StreetActivity model.'''
        model = StreetActivity
        fields = ['name', 'description', 'method', 'question', 'supplies']
        labels = {
            'name': 'Naam van het spel',
            'description': 'Stap-voor-stap handleiding',
            'method': 'Methode van benadering',
            'question': 'Kernvraag',
            'supplies': 'Benodigdheden voor het spel'
        }
        help_texts = {
            'name': 'Vul alsjeblieft de naam van het spel in.',
            'description': 'Geef een stap-voor-stap uitleg hoe je het spel uitvoert.',
            'method': 'Kies hoe je mensen benadert: uitnodigen of aanspreken.',
            'question': 'Formuleer de kernvraag die je gebruikt om mensen uit te nodigen of aan te spreken.',
            'supplies': 'Welke materialen heb je nodig voor dit spel?',
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
                'Jouw reflectie over het doen van dit spel...'}),
        }
        labels = {
            'reflection': 'Hoe denk je terug over het doen van dit spel?',
        }
        help_texts = {
            'reflection': """Wat heb je geleerd? Tips, suggesties?
            Jouw ervaring draagt bij aan het begrijpen van dit spel!""",
        }

    def clean(self):
        """Custom validation to ensure reflection is provided."""
        cleaned_data = super().clean()
        reflection = cleaned_data.get('reflection')

        if not reflection:
            self.add_error('reflection', 'Geen reflectie gegeven')

        return cleaned_data
