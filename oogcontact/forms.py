from django.forms import ModelForm
from .models import Registration

class RegistrationForm(ModelForm):
    """Form for user registration."""
    
    class Meta:
        model = Registration
        fields = ['name', 'email']
        labels = {
            'name': 'Je Naam',
            'email': 'Je Email Adres',
        }
        help_texts = {
            'name': 'Vul alsjeblieft je volledige naam in.',
            'email': 'We gebruiken dit email adres om contact met je op te nemen.',
        }