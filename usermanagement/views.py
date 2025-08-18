from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from .forms import RegisterForm, UserForm, ProfileForm


class Register(CreateView):
    """The sign up functionality"""

    form_class    = RegisterForm
    template_name = "usermanagement/register.html"
    success_url   = reverse_lazy("chat")

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


@login_required
def update_profile(request):
    """When the user navigates to his profile,
    it either gets the forms to update his profile or it post his changed settings"""
    if request.method == "POST":
        user_form    = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ("Bewerken van je profiel is geslaagd!"))
            return redirect("chat")
    else:
        user_form    = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(
        request,
        "auth/user_form.html",
        {"user_form": user_form, "profile_form": profile_form},
    )
