import string
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from sociablecreating.forms import LogMessageForm, SociableForm
from usermanagement.models import Profile
from .models import LogMessage, Sociable


def home(request):
    '''Renders the homepage'''
    return render(request, 'sociablecreating/index.html')


def search_sociable(request):
    '''Given a slug entered by the user,
    redirects the user to the sociable associated'''
    search_code = request.GET.get('search-code').lower()
    try:
        sociable = Sociable.objects.get(slug=search_code)
        if sociable.owner == request.user:
            return redirect('sociable', slug=sociable.slug)
        return display_message_or_code(request, sociable)
    except ObjectDoesNotExist:
        context = {'search_code': search_code}
        return render(request, 'sociablecreating/sociable_not_found.html', context)


def display_message_or_code(request, sociable):
    '''Given a sociable,
    displays the first unread message
    or displays the sociable detail page if there are no unread messages'''
    lst_logmessage = LogMessage.objects.filter(sociable=sociable, is_read=False)
    if lst_logmessage:
        context = {'sociable': sociable, 'message': lst_logmessage[0], 'search-code': sociable.slug}
        return render(request, 'sociablecreating/message.html', context=context)
    else:
        return redirect('sociable', slug=sociable.slug)


def display_code_after_message_is_read(request, pk):
    '''Given the visitor clicks gelezen,
    update the message to read and display code'''
    message = LogMessage.objects.get(id=pk)
    message.is_read = True
    message.save()
    return redirect('sociable', slug=message.sociable)


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
        self.update_xp_and_lvl()
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

    def update_xp_and_lvl(self):
        '''When creating a logmessage,
        update the xp values and lvl when needed
        xp_needed is lvl ^ 1.2
        '''
        user = self.request.user
        if not user.is_anonymous and self.is_first_logmessage():
            profile = Profile.objects.get(user=user)
            profile.xp += 1
            if profile.xp == profile.xp_next_lvl:
                profile.lvl         += 1
                profile.xp_start_lvl = profile.xp_next_lvl
                profile.xp_next_lvl += round(profile.lvl**1.2)
            profile.save()

    def is_first_logmessage(self):
        '''When updating xp and lvl,
        checks if the created logmessage is the first logmessage
        created by the user for this sociable'''
        slug     = super().get_context_data()['view'].kwargs['slug']
        sociable = Sociable.objects.get(slug=slug)
        user     = self.request.user
        return not sociable.logmessage_set.filter(author=user)


class LogMessageDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model = LogMessage
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        '''Only the owner may delete logmessages from their sociable'''
        logmessage = self.get_object()
        sociable   = logmessage.sociable
        return self.request.user.pk == sociable.owner_id

    def get_success_url(self):
        logmessage = self.get_object()
        sociable   = logmessage.sociable
        return reverse("sociable", kwargs={"slug": sociable.slug})


class LogMessageUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView):
    '''Generic editing view to update LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model = LogMessage
    form_class = LogMessageForm

    def test_func(self) -> bool | None:
        '''Both the owner of the sociable and the author may update the sociable'''
        logmessage = self.get_object()
        sociable   = logmessage.sociable
        user_id    = self.request.user.pk
        return logmessage.author_id == user_id or sociable.owner_id == user_id


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
        form.instance.slug  = get_random_string(8, allowed_chars=string.ascii_lowercase+string.digits)

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


class SociableUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView):
    '''Generic editing view to update Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model  = Sociable
    form_class  = SociableForm

    def test_func(self):
        '''Only the owner may update the sociable'''
        sociable = self.get_object()
        return self.request.user.pk == sociable.owner_id


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
