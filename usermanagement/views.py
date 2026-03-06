from django.shortcuts import redirect, render
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.views import View
from core.utils.mixins import ActivityFilterMixin
from streetactivity.models import Word
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
        return redirect(self.success_url)  # type: ignore[reportArgumentType]

class UserDetail(DetailView, ActivityFilterMixin):
    """Generic display view to get to the profile of the user:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model          = User
    slug_field     = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_wordtree_base_filter(self):
        """Base filter: this specific user."""
        user = self.get_object()
        return {
            'type': 'user',
            'value': user.username,
            'display_name': user.get_full_name() or user.username
        }

    def get_base_queryset(self):
        """Base queryset: all words by this user."""
        user = self.get_object()
        return Word.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        """Add word tree data to context"""
        context = super().get_context_data(**kwargs)
        user = self.object
        context = self.add_word_tree_data(user, context)
        return context

    def add_word_tree_data(self, user, context):
        """Given the user,
        returns the context with the wordtree date, user-specific statistics and the user's most used words"""
        # Get current filters from request
        current_filters = {
            'date': self.request.GET.get('date_filter', 'all'),
            'activity': self.request.GET.get('activity_filter', 'all'),
        }

        # Get word tree context (includes activity filters via ActivityFilterMixin)
        wordtree_context = self.get_wordtree_context(
            self.get_base_queryset(),
            current_filters
        )
        context.update(wordtree_context)
        context['wordtree_container_id'] = f"user-{user.username}"

        # User-specific stats
        all_words = self.get_base_queryset()
        context['total_words'] = all_words.count()
        context['unique_words'] = all_words.values('word').distinct().count()

        # Get user's most used words
        context['top_words'] = all_words.values('word')\
            .annotate(count=Count('word'))\
            .order_by('-count')[:5]

        return context

class ProfileUpdateView(LoginRequiredMixin, View):
    """View for user to update its profile"""
    template_name = "auth/user_form.html"

    def get(self, request, *args, **kwargs):
        """Display both User and ProfileForm"""
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form})

    def post(self, request, *args, **kwargs):
        """Handle POST for both user and profile form,
        allowing partial success with appropriate messages."""
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        # Check if both forms are valid
        user_valid = user_form.is_valid()
        profile_valid = profile_form.is_valid()

        if user_valid and profile_valid:
            # Both forms valid, save both
            user_form.save()
            profile_form.save()
            messages.success(request, "Bewerken van je profiel is geslaagd!")
            return redirect("user", username=request.user.username)

        elif user_valid and not profile_valid:
            # User form valid, profile form invalid - save user but show profile errors
            user_form.save()
            messages.warning(request, "Profielgegevens zijn niet opgeslagen vanwege fouten.")

        elif not user_valid and profile_valid:
            # Profile form valid, user form invalid - save profile but show user errors
            profile_form.save()
            messages.warning(request, "Gebruikersgegevens zijn niet opgeslagen vanwege fouten.")

        # If neither form was valid, or we have partial success, re-render with errors
        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form})

def add_xp(profile):
    """Given  the user profile, 
    add 50 xp to the user profile"""
    profile.xp += 50

def update_lvl(profile):
    """Given the user profile,
    update the lvl and xp_start, xp_next_lvl if xp exceeds the treshold for next lvl"""
    while profile.xp >= profile.xp_next_lvl:
        profile.lvl += 1
        profile.xp_start = profile.xp_next_lvl
        profile.xp_next_lvl = int(100*pow(profile.lvl,1.7))

def calc_xp_percentage(profile):
    """Given the total xp, the xp at the start of the level and the xp treshold for the new level,
    calculate the percentage of the xp the user acquired during this level,
    so that it can be used in the progress bar"""
    xp_acquired_in_this_lvl = profile.xp - profile.xp_start
    total_xp_needed_for_next_lvl = profile.xp_next_lvl   - profile.xp_start
    profile.xp_percentage_of_progress = xp_acquired_in_this_lvl/total_xp_needed_for_next_lvl*100
