from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from streetactivity.views import CONFIRM_DELETE_TEMPLATE
from weaktie.forms import ContactChannelForm, LinkForm, WhereaboutForm
from weaktie.models import ContactChannel, Link, Whereabout


class WhereaboutCreateView(LoginRequiredMixin, generic.CreateView):
    """View for creating a Whereabout instance."""
    model = Whereabout
    form_class = WhereaboutForm

    def get_initial(self):
        """Set the initial when to the current date and time."""
        initial = super().get_initial()
        initial['when'] = timezone.localtime()
        return initial

    def form_valid(self, form):
        """Save the form and associate it with the current user."""
        whereabout = form.save(commit=False)
        whereabout.user = self.request.user
        whereabout.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user-profile', kwargs={'username': user.username})

class WhereaboutUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """View for updating a Whereabout instance."""
    model = Whereabout
    form_class = WhereaboutForm

    def test_func(self):
        """Check if the current user is the owner of the Whereabout instance."""
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        """Raise PermissionDenied if the user is authenticated
        but not the owner of the Whereabout instance."""
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def get_success_url(self):
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user-profile', kwargs={'username': user.username})

class WhereaboutDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """View for updating a Whereabout instance."""
    model = Whereabout
    template_name = CONFIRM_DELETE_TEMPLATE

    def test_func(self):
        """Check if the current user is the owner of the Whereabout instance."""
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        """Raise PermissionDenied if the user is authenticated
        but not the owner of the Whereabout instance."""
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def get_success_url(self):
        """Redirect to the profile page after successful deletion."""
        user = self.request.user
        return reverse('user-profile', kwargs={'username': user.username})

class LinkCreateView(LoginRequiredMixin, generic.CreateView):
    """View for creating a Link instance."""
    model = Link
    form_class = LinkForm

    def form_valid(self, form):
        """Save the form and associate it with the current user."""
        link = form.save(commit=False)
        link.user = self.request.user
        link.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user-profile', kwargs={'username': user.username})

class LinkDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """View for deleting a Link instance."""
    model = Link
    template_name = CONFIRM_DELETE_TEMPLATE

    def test_func(self):
        """Check if the current user is the owner of the Link instance."""
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        """Raise PermissionDenied if the user is authenticated
        but not the owner of the Link instance."""
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def get_success_url(self):
        """Redirect to the profile page after successful deletion."""
        user = self.request.user
        return reverse('user-profile', kwargs={'username': user.username})

class ContactChannelCreateView(LoginRequiredMixin, generic.CreateView):
    """View for creating a ContactChannel instance."""
    model = ContactChannel
    form_class = ContactChannelForm

    def form_valid(self, form):
        """Save the form and associate it with the current user."""
        link = form.save(commit=False)
        link.user = self.request.user
        link.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user-chatactivity', kwargs={'username': user.username})

class ContactChannelDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """View for deleting a ContactChannel instance."""
    model = ContactChannel
    template_name = CONFIRM_DELETE_TEMPLATE

    def test_func(self):
        """Check if the current user is the owner of the ContactChannel instance."""
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        """Raise PermissionDenied if the user is authenticated
        but not the owner of the ContactChannel instance."""
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def get_success_url(self):
        """Redirect to the profile page after successful deletion."""
        user = self.request.user
        return reverse('user-chatactivity', kwargs={'username': user.username})


QUESTION_OF_THE_WEEK = {
    "text": "Als je moest vechten tegen 100 paarden ter grootte van een eend of tegen één eend ter grootte van een paard, voor wie zou je kiezen en waarom?",
    "source_name": "Aha Slides",
    "source_url": "https://ahaslides.com/nl/blog/weird-questions-to-ask/",
}

class UserChatActivityView(generic.TemplateView):
    """Show the chat activity invitation page for a user.

    The page is public: anyone can view it via the username in the URL.
    Owner-only controls (add/delete contact channels) are rendered in the
    template based on ``request.user == user``.
    """

    template_name = "weaktie/user_chatactivity.html"

    def get_context_data(self, **kwargs):
        """Add the user, their contact channels and the question of the week.

        Returns:
            dict: The template context.
        """
        context = super().get_context_data(**kwargs)

        user_model = get_user_model()
        user = get_object_or_404(
            user_model, username=self.kwargs["username"]
        )

        context["user"] = user
        context["contactchannels"] = user.contactchannels.all()
        context["question"] = QUESTION_OF_THE_WEEK

        return context

class UserChatActivityAlternativeView(UserChatActivityView):
    """Show the chat activity invitation page for a user.

    This is an alternative view that uses a different template.
    """

    template_name = "weaktie/user_chatactivity_alternative.html"
