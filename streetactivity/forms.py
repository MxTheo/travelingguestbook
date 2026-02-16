from django import forms
from .models import StreetActivity, Moment, Experience, ConfidenceLevel

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

    confidence_level = forms.ChoiceField(
        choices=ConfidenceLevel.choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Hoe zelfverzekerd voelde je je?',
        initial=ConfidenceLevel.ONZEKER,
    )

    class Meta:
        model = Moment
        fields = ['confidence_level', 'report']
        widgets = {
            'report': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder':
                'Omschrijf maximaal 1 reden...'}),
        }
        labels = {
            'confidence_level': 'Hoe zelfverzekerd voelde je je?',
            'report': 'Ik voelde mij zo, omdat ... *',
        }
        help_texts = {
            'report': 'Deel 1 belangrijk moment voor jou in maximaal 367 karakters. Is je verhaal langer? Overweeg dan om het op te splitsen in meerdere momenten zodat elk moment duidelijk blijft',
        }

    def clean(self):
        """Custom validation to ensure report is provided."""
        cleaned_data = super().clean()
        report = cleaned_data.get('report')

        if not report:
            self.add_error('report', 'Geen reden gegeven. Hoe komt het dat je je zo voelde?')

        return cleaned_data

class AddMomentForm(MomentForm):
    """Form to add a moment to an experience, inherits from MomentForm."""
    class Meta(MomentForm.Meta):
        """Only override the report, so that it is clearer that this moment is one of many."""
        widgets = {
            **MomentForm.Meta.widgets,
            'report': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
                'placeholder':
                'Omschrijf maximaal 1 reden...'}),
        }
        help_texts = {
            **MomentForm.Meta.help_texts,
            'report': 'Omschrijf 1 specifieke reden in maximaal 367 karakters. Heb je meerdere redenen? Maak dan meerdere momenten aan, zodat de verandering van je zelfverzekerdheid inzichtelijk wordt'
        }

class ExperienceForm(forms.ModelForm):
    """Form to create an experience with moments"""
    class Meta:
        """No fields as experience is just a container for moments"""
        model = Experience
        fields: list[str] = []
