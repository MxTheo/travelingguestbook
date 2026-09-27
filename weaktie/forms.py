from django import forms
from django.utils import timezone

from weaktie.models import Link, Whereabout


class WhereaboutForm(forms.ModelForm):
    """Form for creating a Whereabout instance."""
    when = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'form-control'},
        ),
        label='Wanneer ga je?',
        help_text='Voer de datum en tijd in van die activiteit',
    )

    class Meta:
        model = Whereabout
        fields = ['location', 'when']
        labels = {
            'location': 'Waar ga je naartoe?',
        }
        help_texts = {
            'location': 'Voer de plek in van de activiteit waar je bij bent',
        }

class LinkForm(forms.ModelForm):
    """Form for creating a Link instance."""
    url = forms.URLField(
        max_length=500,
        assume_scheme="https",
        label="Waar ben je te vinden?",
        help_text='Voeg een link toe naar je sociale media profiel of website, beginnend met https://'
        )

    class Meta:
        model = Link
        fields = ['url']
