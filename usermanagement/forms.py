from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
