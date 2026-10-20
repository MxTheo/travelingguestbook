from django import forms
from django.utils import timezone

from weaktie.models import ContactChannel, Link, Whereabout


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
    source = forms.URLField(
        max_length=500,
        assume_scheme="https",
        required=False,
        label='Waar heb je deze activiteit gevonden? (optioneel)',
        help_text='Voer de URL in van de bron van de activiteit, beginnend met https://',
    )

    class Meta:
        model = Whereabout
        fields = ['location', 'when', 'source']
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

class ContactChannelForm(forms.ModelForm):
    """Form to create or update a ContactChannel.

    The ``app_other`` field is only required when the user selects
    ``ContactChannel.App.OTHER`` as the app. When another app is selected,
    ``app_other`` is cleared so that ``display_app`` always returns a
    sensible value.
    """

    url = forms.URLField(
        max_length=500,
        assume_scheme="https",
        label="Uitnodigingslink van de chat app",
        help_text='Voer de uitnodigingslink in van de chat app die je gebruikt, beginnend met https://',
    )

    class Meta:
        """Configure the form fields and widgets for ContactChannel."""

        model = ContactChannel
        fields = ["app", "app_other", "url"]
        widgets = {
            "app": forms.Select(attrs={"class": "form-select"}),
            "app_other": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Signal",
                }
            ),
        }
        labels = {
            "app": "Welke chat app gebruik je?",
            "app_other": "Hoe heet de app die je gebruikt?",
        }
        help_texts = {
            "app_other": "Vul dit veld alleen in als je 'Anders' hebt geselecteerd bij de chat app.",
        }

    def clean(self):
        """Validate that ``app_other`` is filled in only for the 'Other' app.

        Returns:
            dict: The cleaned data.

        Raises:
            forms.ValidationError: If ``app_other`` is missing when 'Other' is
                selected, or if it is filled in for a known app.
        """
        cleaned_data = super().clean()
        app = cleaned_data.get("app")
        app_other = (cleaned_data.get("app_other") or "").strip()

        if app == ContactChannel.App.OTHER:
            if not app_other:
                self.add_error(
                    "app_other",
                    "Vul de naam van de app in die je gebruikt.",
                )
            else:
                cleaned_data["app_other"] = app_other
        else:
            # Ignore any leftover value so display_app stays consistent.
            cleaned_data["app_other"] = ""

        return cleaned_data