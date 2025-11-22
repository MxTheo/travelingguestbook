from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.views import View
from .forms import RegisterForm, UserForm, ProfileForm


class Register(CreateView):
    """The sign up functionality"""

    form_class    = RegisterForm
    template_name = "usermanagement/register.html"
    success_url   = reverse_lazy("home")

    def form_valid(self, form):
        """After the user input is valid, it logs in and redirects towards its dashboard"""
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

class UserDetail(DetailView):
    """Generic display view to get to the profile of the user:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model          = User
    slug_field     = "username"
    slug_url_kwarg = "username"

class ProfileUpdateView(LoginRequiredMixin, View):
    """View for user to update its profile"""
    template_name = "auth/user_form.html"

    def get(self, request, *args, **kwargs):
        """Display both User and ProfileForm"""
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})

    def post(self, request, *args, **kwargs):
        """Handle POST for both user and profile form, allow saving profile image even if user form invalid"""
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        saved_any = False

        # Save user form if valid
        if user_form.is_valid():
            user_form.save()
            saved_any = True

        # Save profile form (including uploaded image) if valid
        if profile_form.is_valid():
            profile_form.save()
            saved_any = True

        if saved_any:
            messages.success(request, "Bewerken van je profiel is geslaagd!")
            return redirect("user", username=request.user.username)

        # If neither form was valid, re-render with errors
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})