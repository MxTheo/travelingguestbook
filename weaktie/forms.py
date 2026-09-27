from django import forms
from django.utils import timezone

from weaktie.models import Whereabout


class WhereaboutForm(forms.ModelForm):
    """Form for creating a Whereabout instance."""
    date = forms.DateTimeField(
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
        fields = ['location', 'date']
        labels = {
            'location': 'Waar ga je naartoe?',
        }
        help_texts = {
            'location': 'Voer de plek in van de activiteit waar je bij bent',
        }
