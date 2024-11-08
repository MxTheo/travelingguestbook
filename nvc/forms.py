from django import forms
from django.forms import formset_factory

class ObservationForm(forms.Form):
    observation = forms.CharField(max_length=255, help_text="Houd het kort en beperkt tot 1 handeling of uitspraak wat je obeserveerde bij de ander", label="Ik hoorde je...",)

ObservationFormSet = formset_factory(ObservationForm, extra=7, can_delete=True,)