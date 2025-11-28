from django import forms
from .models import Persona, Problem, Reaction


class PersonaForm(forms.ModelForm):
    """Form for adding/editing a Persona."""

    class Meta:
        "Anonymous users can edit the title, core_question, description and portrait"
        model = Persona
        fields = ["title", "core_question", "description", "portrait"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "core_question": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "portrait": forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'portrait': 'Upload een portret foto voor deze persoonstype (optioneel)',
        }


class ProblemForm(forms.ModelForm):
    """Form for adding/editing a Problem of Persona."""

    class Meta:
        "Anonymous users can edit the description of a problem"
        model = Problem
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Beschrijf het probleem...",
                }
            ),
        }
        labels = {
            "description": "Probleem beschrijving",
        }


class ReactionForm(forms.ModelForm):
    """Form for adding/editing a Reaction of Persona."""

    class Meta:
        "Anonymous users can edit the description of a reaction"
        model = Reaction
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Typ de reactie...",
                }
            ),
        }
        labels = {
            "description": "Reactie tekst",
        }
