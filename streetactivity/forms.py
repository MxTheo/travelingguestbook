from django import forms
from .models import StreetActivity, Word

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

class WordForm(forms.ModelForm):
    """Base form for Word with common fields."""

    class Meta:
        model = Word
        fields = ['word']
        widgets = {
            'word': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
                'placeholder':
                'Jouw word in één woord...'}),
        }
        labels = {
            'word': 'Eén woord. Wat past?',
        }
        help_texts = {
            'word': """Het mag van alles zijn: "licht", "baksteen", "vlieg", "stil", "moed"... 
            Het eerste wat in je opkomt""",
        }

    def clean(self):
        """Custom validation to ensure word is provided."""
        cleaned_data = super().clean()
        word = cleaned_data.get('word')

        if not word:
            self.add_error('word', 'Geen woord gegeven')

        return cleaned_data
