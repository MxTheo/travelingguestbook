from django import forms
from .models import StreetActivity, ExternalReference

class StreetActivityForm(forms.ModelForm):
    """Form for creating or updating a StreetActivity."""

    class Meta:
        '''Model form for the StreetActivity model.'''
        model = StreetActivity
        fields = ['name', 'description', 'method', 'question', 'supplies',
                  'difficulty', 'chance', 'extension', 'needHelp']
        labels = {
            'name': 'Naam van de activiteit',
            'description': 'Beschrijving van de activiteit',
            'method': 'Methode van benadering',
            'question': 'Kernvraag',
            'supplies': 'Benodigdheden voor de activiteit',
            'difficulty': 'Moeilijkheidsgraad (1-5)',
            'chance': 'Kans op contact (1-5)',
            'extension': 'Uitbreiding of variatie op de activiteit',
            'needHelp': 'Experimenteel',
        }
        help_texts = {
            'name': 'Vul alsjeblieft de naam van de activiteit in.',
            'description': 'Geef een korte beschrijving van de activiteit.',
            'method': 'Kies hoe je mensen benadert: uitnodigen of aanspreken.',
            'question': 'Formuleer de kernvraag die je gebruikt om mensen uit te nodigen of aan te spreken.',
            'supplies': 'Welke materialen heb je nodig voor deze activiteit?',
            'difficulty': 'Beoordeel hoe moeilijk het is om deze activiteit uit te voeren (1 = makkelijk, 5 = moeilijk).',
            'chance': 'Beoordeel de kans op contact met vreemden (1 = laag, 5 = hoog).',
            'extension': 'Beschrijf mogelijke uitbreidingen of variaties op de activiteit.',
            'needHelp': 'Vink dit aan als de activiteit nog in ontwikkeling is.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'supplies': forms.Textarea(attrs={'rows': 3}),
            'extension': forms.Textarea(attrs={'rows': 3}),
        }

class ExternalReferenceForm(forms.ModelForm):
    """Form for creating an ExternalReference related to a StreetActivity."""

    class Meta:
        '''Model form for the ExternalReference model.'''
        model = ExternalReference
        fields = ['title', 'description', 'url', 'reference_type', 'submitted_by']
        labels = {
            'title': 'Titel van de referentie',
            'description': 'Korte beschrijving van de referentie',
            'url': 'URL van de referentie (indien beschikbaar)',
            'reference_type': 'Type referentie',
            'submitted_by': 'Naam van de indiener (optioneel)',
        }
        help_texts = {
            'title': 'Vul de titel van de referentie in.',
            'description': 'Geef een korte beschrijving van de referentie.',
            'url': 'Voer de URL in als het een online bron is. Laat leeg voor boeken of theorieën.',
            'reference_type': 'Kies het type referentie: persoonlijke ervaring, boek, theorie, etc.',
            'submitted_by': 'Je naam (optioneel). Laat leeg voor anonieme inzendingen.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
