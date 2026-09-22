from django import forms

from gettogether.models import GetTogether


class GetTogetherForm(forms.ModelForm):
    """Form for creating a GetTogether instance."""
    class Meta:
        model = GetTogether
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
