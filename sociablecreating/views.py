import string
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from sociablecreating.forms import LogMessageForm, SociableForm
from .models import LogMessage, Sociable

def home(request):
    '''Renders the homepage'''
    return render(request, 'sociablecreating/index.html')

def search_sociable(request):
    '''Given a slug entered by the user,
    redirects the user to the sociable associated'''
    if request.GET.get('search-code'):
        search_code = request.GET.get('search-code') 
        return redirect('sociable', slug=search_code)
    else:
        return HttpResponse('Nothing found')

def get_logmessage_list_from_sociable_list(sociable_list):
    '''Given a sociable list,
    returns all the log messages from all the sociables in the list'''
    logmessage_list = []
    for sociable in sociable_list:
        logmessage_list.extend(sociable.logmessage_set.all())
    return logmessage_list

class LogMessageCreate(generic.edit.CreateView, LoginRequiredMixin):
    '''Generic editing view to create LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    form_class = LogMessageForm
    model      = LogMessage

    def form_valid(self, form):
        self.set_sociable_relationship(form)
        return super(LogMessageCreate, self).form_valid(form)

    def set_sociable_relationship(self, form):
        '''Given the log message and the sociable slug from the context,
        sets the sociable relationship for the created log message'''
        slug                   = super().get_context_data()['view'].kwargs['slug']
        print('slug = ')
        print(slug)
        sociable               = Sociable.objects.get(slug=slug)
        form.instance.sociable = sociable

class LogMessageDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model = LogMessage
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        logmessage = LogMessage.objects.get(id = self.kwargs['pk'])
        sociable   = logmessage.sociable
        return self.request.user == sociable.owner

    def get_success_url(self):
        logmessage = LogMessage.objects.get(id = self.kwargs['pk'])
        sociable   = logmessage.sociable
        return reverse("sociable", kwargs={"slug": sociable.slug})


class SociableCreate(LoginRequiredMixin, generic.edit.CreateView):
    '''Generic editing view to create Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    form_class  = SociableForm
    model       = Sociable
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.slug  = get_random_string(8,
        allowed_chars = string.ascii_lowercase + string.digits)
        messages.success(self.request, 'Sociable has been created successfully.')
        return super(SociableCreate, self).form_valid(form)

class SociableUpdate(UserPassesTestMixin, generic.edit.UpdateView):
    '''Generic editing view to update Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model  = Sociable
    fields = ['description']

    def test_func(self):
        sociable = Sociable.objects.get(slug = self.kwargs['slug'])
        return self.request.user == sociable.owner

class SociableDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model         = Sociable
    success_url   = reverse_lazy('dashboard')
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        sociable = Sociable.objects.get(slug = self.kwargs['slug'])
        return self.request.user == sociable.owner


class SociableDetail(generic.DetailView):
    '''Generic display view to show detailpage of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model = Sociable

class SociableList(generic.ListView):
    '''Generic display view to show an overview of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model = Sociable
