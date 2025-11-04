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
class BaseExperienceForm(forms.ModelForm):
    """Base form for Experience with common fields."""
    
    class Meta:
        model = Experience
        fields = ['fase', 'tags', 'report', 'external_link']
        widgets = {
            'report': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Omschrijf je innerlijke beleving...'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control'}),
            'fase': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

class PasserbyExperienceForm(BaseExperienceForm):
    """Simplified form for passersby - category and tags first."""
    
    class Meta(BaseExperienceForm.Meta):
        labels = {
            'fase': 'Hoe zelfverzekerd voelde je je?',
            'tags': 'Welke woorden passen bij je ervaring?',
            'report': 'Wil je iets toevoegen? (optioneel)',
            'external_link': 'Link naar meer informatie (optioneel)',
        }
        help_texts = {
            'tags': 'Kies 3 tags die je ervaring weergeven',
            'report': 'Een beschrijving van wat er gebeurde',
            'external_link': '',
        }

class PractitionerExperienceForm(BaseExperienceForm):
    """Detailed form for practitioners - reflection first."""
    
    class Meta(BaseExperienceForm.Meta):
        labels = {
            'fase': 'Hoe zelfverzekerd voelde je je?',
            'tags': 'Welke thema\'s komen naar voren?',
            'report': 'Jouw reflectie op deze ervaring',
            'external_link': 'Link naar verdere reflectie (optioneel)',
        }
        help_texts = {
            'tags': 'Kies tags die de kern van je ervaring raken',
            'report': 'Deel wat je waarnam - in jezelf en om je heen',
            'external_link': 'Link naar je blog of iets anders',
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
