from django.shortcuts import render
from django.urls import reverse

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from contact.views import create_mailto_url
from .models import Registration

def oogcontact_home(request):
    """Renders the homepage of oogcontact course."""
    mailto_url = create_mailto_url()
    context    = {"mailto_url": mailto_url}
    return render(request, "oogcontact/oogcontact_home.html", context)

class RegistrationListView(generic.ListView, LoginRequiredMixin):
    """View to list all registrations."""
    model = Registration
    template_name = "oogcontact/registration_list.html"
    context_object_name = "registrations"
    paginate_by = 10  # Number of registrations per page
    ordering = ['-date_created']  # Order by date created, newest first

class RegistrationDetailView(generic.DetailView):
    """View to display details of a single registration."""
    model = Registration
    template_name = "oogcontact/registration_detail.html"
    context_object_name = "registration"

    def get_context_data(self, **kwargs):
        """Add additional context data to the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration Details'
        return context

class RegistrationCreateView(generic.CreateView):
    """View to create a new registration."""
    model = Registration
    fields = ['name', 'email']
    template_name = "oogcontact/registration_form.html"

    def get_success_url(self):
        return reverse('registration_detail', args=[self.object.pk])

    def form_valid(self, form):
        """If the form is valid, save the registration and redirect."""
        return super().form_valid(form)


class RegistrationUpdateView(generic.UpdateView, LoginRequiredMixin):
    """View to update an existing registration."""
    model = Registration
    fields = ['name', 'email', 'hasCanceled']
    template_name = "oogcontact/registration_form.html"

    def get_success_url(self):
        return reverse('registration_detail', args=[self.object.pk])

    def form_valid(self, form):
        """If the form is valid, save the updated registration and redirect."""
        return super().form_valid(form)
