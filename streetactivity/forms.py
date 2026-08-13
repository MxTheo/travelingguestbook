from django import forms
from django.core.exceptions import ValidationError

from .models import Reflection, StreetActivity, StreetActivityPhoto


class StreetActivityForm(forms.ModelForm):
    """Form for a StreetActivity."""

    class Meta:
        '''Model form for the StreetActivity model.'''
        model = StreetActivity
        fields = ['name', 'description', 'method', 'question', 'supplies']
        labels = {
            'name': 'Naam van het spel',
            'description': 'Stap-voor-stap handleiding',
            'method': 'Methode van benadering',
            'question': 'Kernvraag',
            'supplies': 'Benodigdheden voor het spel'
        }
        help_texts = {
            'name': 'Vul alsjeblieft de naam van het spel in.',
            'description': 'Geef een stap-voor-stap uitleg hoe je het spel uitvoert.',
            'method': 'Kies hoe je mensen benadert: uitnodigen of aanspreken.',
            'question': 'Formuleer de kernvraag die je gebruikt om mensen uit te nodigen of aan te spreken.',
            'supplies': 'Welke materialen heb je nodig voor dit spel?',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'supplies': forms.Textarea(attrs={'rows': 3}),
        }

class ReflectionForm(forms.ModelForm):
    """Base form for Reflection with common fields."""

    class Meta:
        model = Reflection
        fields = ['reflection']
        widgets = {
            'reflection': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder':
                'Jouw reflectie over het doen van dit spel...'}),
        }
        labels = {
            'reflection': 'Hoe denk je terug over het doen van dit spel?',
        }
        help_texts = {
            'reflection': """Wat heb je geleerd? Tips, suggesties?
            Jouw ervaring draagt bij aan het begrijpen van dit spel!""",
        }

    def clean(self):
        """Custom validation to ensure reflection is provided."""
        cleaned_data = super().clean()
        reflection = cleaned_data.get('reflection')

        if not reflection:
            self.add_error('reflection', 'Geen reflectie gegeven')

        return cleaned_data

class StreetActivityPhotoForm(forms.ModelForm):
    """Form for uploading a photo related to a StreetActivity."""
    class Meta:
        model = StreetActivityPhoto
        fields = ['image']

    def clean_image(self):
        """
        Validation for the image field:
        - Check if the file is an image (JPG, JPEG, PNG).
        - Check if the file size is not too large (default 5MB).
        """
        image = self.cleaned_data.get('image')
        if image:
            try:
                self.check_image_size(image)
                self.check_image_type(image)
            except ValidationError as e:
                raise ValidationError(e.message)

        return image

    def check_image_type(self, image):
        """Check if the uploaded file is an image (JPG, JPEG, PNG)."""
        valid_extensions = ['jpg', 'jpeg', 'png']
        if image.name.split('.')[-1].lower() not in valid_extensions:
            raise ValidationError("Alleen JPG, JPEG en PNG bestanden zijn toegestaan.")

    def check_image_size(self, image):
        """Check if the uploaded image file size is not too large (default 5MB)."""
        max_size = 5 * 1024 * 1024  # 5MB
        if image.size > max_size:
            raise ValidationError(f"Bestand is te groot.")