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
        label='Hoe was je zelfvertrouwen in dat moment?',
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
                'Omschrijf 1 reden...'}),
        }
        labels = {
            'report': 'Ik voelde mij (on)zeker, omdat ...',
        }
        help_texts = {
            'report': 'Je hebt hier ruimte voor ongeveer 3 à 4 zinnen om te vertellen wat jouw zelfvertrouwen op dat moment beïnvloedde. Schrijf gewoon wat als eerste bij je opkomt, het hoeft niet perfect te zijn.',
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
                'Omschrijf 1 reden...'}),
        }
