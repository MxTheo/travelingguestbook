from django import forms

from weaktie.models import Whereabout


class WhereaboutForm(forms.ModelForm):
    """Form for creating a Whereabout instance."""
    class Meta:
        model = Whereabout
        fields = ['location', 'date']
        labels = {
            'location': 'Waar wil je de samenkomst doen?',
            'date': 'Wanneer wil je de samenkomst doen?',
        }
        help_texts = {
            'location': 'Voer de locatie in waar de samenkomst zal plaatsvinden.',
            'date': 'Voer de datum in voor de samenkomst.',
        }
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
