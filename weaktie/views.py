from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from streetactivity.views import CONFIRM_DELETE_TEMPLATE
from weaktie.forms import WhereaboutForm, LinkForm
from weaktie.models import Whereabout, Link


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
        return reverse('user', kwargs={'username': user.username})

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
        return reverse('user', kwargs={'username': user.username})

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
        return reverse('user', kwargs={'username': user.username})

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
        return reverse('user', kwargs={'username': user.username})

class LinkUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """View for updating a Link instance."""
    model = Link
    form_class = LinkForm

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
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user', kwargs={'username': user.username})

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
        return reverse('user', kwargs={'username': user.username})
