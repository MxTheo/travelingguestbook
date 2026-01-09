from django import forms
from .models import StreetActivity, Moment, Experience

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
        fields = ['confidence_level', 'report', 'keywords']
        widgets = {
            'confidence_level': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'report': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder':
                'Omschrijf je innerlijke beleving...'}),
            'keywords': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
                'placeholder':
                "Energiek, ongeduldig, vertrouwen..."}),
        }
        labels = {
            'confidence_level': 'Hoe zelfverzekerd voelde je je?',
            'report': 'Wat was de reden? Wat deed dat met je?',
            'keywords': "3 woorden uit wat je net hebt geschreven, gescheiden door komma's",
        }
        help_texts = {
            'report': 'Vertel iets over je (on)zekerheid in maximaal 3500 karakters',
            'keywords': "3 woorden, gescheiden door komma's",
        }

class AddMomentToExperienceForm(MomentForm):
    """Form to add a moment to an experience."""
    class Meta(MomentForm.Meta):
        fields = MomentForm.Meta.fields + ['activity']
        labels = MomentForm.Meta.labels.copy()
        labels.update({
            'activity': 'Wat heb je gedaan?',
        })
        help_texts = MomentForm.Meta.help_texts.copy()

class ExperienceForm(forms.ModelForm):
    """Form to create an experience with moments"""
    class Meta:
        """No fields as experience is just a container for moments"""
        model = Experience
        fields = []
