from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from usermanagement.models import Profile

class RegisterForm(UserCreationForm):
    '''Form for registration, where the attributes are inherited from user and email is added'''
    first_name = forms.CharField(max_length=100, help_text='Not required. If not entered, then your username will be displayed on your sociable pages', required=False)
    last_name = forms.CharField(max_length=100, help_text='Not required. It is optional, so that your name will be displayed on your sociable pages', required=False)
    email = forms.EmailField(max_length=150, required=True, help_text='Required. 150 characters or fewer. Please enter a valid address with @')

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location']