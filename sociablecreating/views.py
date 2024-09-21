import string
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from sociablecreating.forms import LogMessageForm, SociableForm
from .models import LogMessage, Sociable
from usermanagement.models import Profile


def home(request):
    '''Renders the homepage'''
    return render(request, 'sociablecreating/index.html')


def search_sociable(request):
    '''Given a slug entered by the user,
    redirects the user to the sociable associated'''
    search_code = request.GET.get('search-code')
    if search_code:
        search_code = search_code.lower()
        if Sociable.objects.filter(slug=search_code):
            return redirect('sociable', slug=search_code)
    context = {'search_code': search_code}
    return render(request, 'sociablecreating/sociable_not_found.html', context)


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

    def get_initial(self):
        '''If logged in, the username is entered as initial value of name'''
        initial = super().get_initial()
        user    = self.request.user
        if not user.is_anonymous:
            initial['name'] = user.username
        return initial

    def form_valid(self, form):
        '''After the form is valid, set the relationships'''
        self.set_sociable(form)
        self.set_author(form)
        return super(LogMessageCreate, self).form_valid(form)

    def set_author(self, form):
        '''Given the logmessage and the user,
        sets the user as the author, if user is logged in'''
        user = self.request.user
        if not user.is_anonymous:
            form.instance.author = user

    def set_sociable(self, form):
        '''Given the log message and the sociable slug from the context,
        sets the sociable relationship for the created log message'''
        slug                   = super().get_context_data()['view'].kwargs['slug']
        sociable               = Sociable.objects.get(slug=slug)
        form.instance.sociable = sociable


class LogMessageDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model = LogMessage
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        logmessage = LogMessage.objects.get(id=self.kwargs['pk'])
        sociable   = logmessage.sociable
        return self.request.user == sociable.owner

    def get_success_url(self):
        logmessage = LogMessage.objects.get(id=self.kwargs['pk'])
        sociable   = logmessage.sociable
        return reverse("sociable", kwargs={"slug": sociable.slug})


class SociableCreate(LoginRequiredMixin, generic.edit.CreateView):
    '''Generic editing view to create Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    form_class  = SociableForm
    model       = Sociable
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        self.set_autocalculated_attributes(form)
        self.save_description_as_default(form)
        return super(SociableCreate, self).form_valid(form)

    def set_autocalculated_attributes(self, form):
        '''Sets the attributes that are automatically determined, which are
         - Owner
         - Slug'''
        form.instance.owner = self.request.user
        form.instance.slug  = get_random_string(8, allowed_chars=string.ascii_lowercase + string.digits)

    def get_initial(self):
        '''When creating a sociable, sets the initial values for descrition'''
        initial = super().get_initial()
        self.set_description(initial)
        return initial

    def set_description(self, initial):
        '''Given the profile of the user, sets the description the user entered in their profile'''
        profile    = Profile.objects.get(user=self.request.user)
        cust_descr = profile.custom_description_for_code.strip()
        if cust_descr != '':
            initial['description'] = cust_descr

    def save_description_as_default(self, form):
        '''Given that the user checked to save description as their default description,
        saves the description in their profile'''
        is_default_description = form.cleaned_data.get('is_default_description')
        if is_default_description:
            profile = Profile.objects.get(user=self.request.user)
            profile.custom_description_for_code = form.cleaned_data.get('description')
            profile.save()


class SociableUpdate(UserPassesTestMixin, generic.edit.UpdateView):
    '''Generic editing view to update Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model  = Sociable
    fields = ['description']

    def test_func(self):
        sociable = Sociable.objects.get(slug=self.kwargs['slug'])
        return self.request.user == sociable.owner


class SociableDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model         = Sociable
    success_url   = reverse_lazy('dashboard')
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        sociable = Sociable.objects.get(slug=self.kwargs['slug'])
        return self.request.user == sociable.owner


class SociableDetail(generic.DetailView):
    '''Generic display view to show detailpage of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model = Sociable


class SociableList(generic.ListView):
    '''Generic display view to show an overview of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model = Sociable
