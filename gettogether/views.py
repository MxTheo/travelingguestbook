from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views import generic

from gettogether.forms import GetTogetherForm
from gettogether.models import GetTogether
from streetactivity.views import CONFIRM_DELETE_TEMPLATE


class GetTogetherCreateView(LoginRequiredMixin, generic.CreateView):
    """View for creating a GetTogether instance."""
    model = GetTogether
    form_class = GetTogetherForm

    def form_valid(self, form):
        """Save the form and associate it with the current user."""
        get_together = form.save(commit=False)
        get_together.user = self.request.user
        get_together.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user', kwargs={'username': user.username})

class GetTogetherUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """View for updating a GetTogether instance."""
    model = GetTogether
    form_class = GetTogetherForm

    def test_func(self):
        """Check if the current user is the owner of the GetTogether instance."""
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        """Raise PermissionDenied if the user is authenticated
        but not the owner of the GetTogether instance."""
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def get_success_url(self):
        """Redirect to the profile page after successful form submission."""
        user = self.request.user
        return reverse('user', kwargs={'username': user.username})

class GetTogetherDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """View for updating a GetTogether instance."""
    model = GetTogether
    template_name = CONFIRM_DELETE_TEMPLATE

    def test_func(self):
        """Check if the current user is the owner of the GetTogether instance."""
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        """Raise PermissionDenied if the user is authenticated
        but not the owner of the GetTogether instance."""
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def get_success_url(self):
        """Redirect to the profile page after successful deletion."""
        user = self.request.user
        return reverse('user', kwargs={'username': user.username})
