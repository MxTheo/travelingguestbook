from django import forms
from .models import PartnershipRequest
class PartnershipRequestForm(forms.ModelForm):
    """Form for to request streetpartnership"""
    class Meta:
        model = PartnershipRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'maxlength': '300',
                'placeholder': 'Stel jezelf voor...',
                'class': 'form-control'
            }),
        }
        labels = {
            'message': 'Bericht (optioneel)'
        }
        help_texts = {
            'message': 'Max 300 tekens. Alleen zichtbaar voor de uitgenodigde speler'
        }

class EndPartnershipForm(forms.Form):
    """Eenvoudig form om partnerschap te beëindigen"""
    confirm = forms.BooleanField(
        required=True,
        label="Ik wil dit partnerschap beëindigen",
        help_text="Dit kan niet ongedaan worden gemaakt"
    )
