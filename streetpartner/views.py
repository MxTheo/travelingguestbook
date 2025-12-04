from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
)
from .models import PartnershipRequest
from .forms import PartnershipRequestForm

class SendPartnershipRequestView(LoginRequiredMixin, CreateView):
    """Createview to request a partnership to a user"""
    model = PartnershipRequest
    form_class = PartnershipRequestForm
    template_name = 'streetpartner/send_request.html'

    def get_form_kwargs(self):
        """Set from_user and to_user before validation"""
        kwargs = super().get_form_kwargs()
        if kwargs['instance'] is None:  # only on creation
            kwargs['instance'].from_user = self.request.user
            kwargs['instance'].to_user = get_object_or_404(
                User,
                username=self.kwargs.get('username')
            )
        return kwargs

    def form_valid(self, form):
        """Validation is done on the clean method on the model"""
        """Zet de users op het instance object"""
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        """Redirect to the profile page of the user"""
        return self.object.to_user.profile.get_absolute_url()
