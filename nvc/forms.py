from django import forms
from django.forms import formset_factory

class ObservationForm(forms.Form):
    """Single line where the user can enter an observation of what the other said or did"""
    observation = forms.CharField(
        max_length=255,
        label='',
        required=False,
        initial='Ik hoorde je zeggen ',
        widget=forms.TextInput(attrs={'placeholder': 'Ik hoorde je zeggen...'}),
        )

ObservationFormSet = formset_factory(ObservationForm, extra=7)
