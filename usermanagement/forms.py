from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django import forms


class RegisterForm(UserCreationForm):
    """Form for registration, where the attributes are inherited from user and email is added"""

    class Meta:
        model  = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

class UserForm(forms.ModelForm):
    """UserForm and ProfileForm are both shown on a page. The UserForm is for the attributes of the UserModel"""

    class Meta:
        model  = User
        fields = ["email"]


class ProfileForm(forms.ModelForm):
    """UserForm and ProfileForm are both shown on a page. The ProfileForm is for the attributes of the ProfileModel"""

    class Meta:
        model  = Profile
        fields = ["lvl"]
