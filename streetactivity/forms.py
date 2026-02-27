from django import forms
from .models import StreetActivity, Moment

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

class MomentForm(forms.ModelForm):
    """Base form for Moment with common fields."""

    class Meta:
        model = Moment
        fields = ['word']
        widgets = {
            'word': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
                'placeholder':
                'Jouw moment in één woord...'}),
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
