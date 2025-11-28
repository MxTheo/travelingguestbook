import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    """Form for registration, where the attributes are inherited from user and email is added"""
    class Meta:
        """Fields required for registering as a user"""
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]


class UserForm(forms.ModelForm):
    """UserForm and ProfileForm are both shown on a page. 
    The UserForm is for the attributes of the UserModel"""

    email = forms.EmailField(
        required=True,
        error_messages={
            "invalid": "Vul een echt e‑mailadres in.",
            "required": "E‑mail is verplicht.",
        },
        widget=forms.EmailInput(attrs={"placeholder": "jouw@voorbeeld.nl"}),
    )

    class Meta:
        """E-mail is editable"""
        model = User
        fields = ["email"]


class ProfileForm(forms.ModelForm):
    """UserForm and ProfileForm are both shown on a page. 
    The ProfileForm is for the attributes of the ProfileModel"""

    class Meta:
        """Profile_image is editable"""
        model = Profile
        fields = ["profile_image"]

    def clean_profile_image(self):
        """Validate the image size and the filetype"""
        image = self.cleaned_data.get("profile_image")
        if image:
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    "Ongeldige bestandsextensie. Toegestaan: JPG, JPEG, PNG, GIF, WebP"
                )

            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise forms.ValidationError("Afbeelding mag niet groter zijn dan 5MB")

        return image
