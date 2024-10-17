import string
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from sociablecreating.forms import LogMessageForm
from usermanagement.models import Profile, User
from .models import LogMessage, Sociable


def home(request):
    '''Renders the homepage'''
    return render(request, 'sociablecreating/index.html')


def search_sociable(request):
    '''Given a slug entered by the user,
    redirects the user to the sociable associated'''
    search_code = request.GET['search-code'].lower()
    try:
        sociable = Sociable.objects.get(slug=search_code)
        if sociable.owner == request.user:
            return redirect('sociable', slug=sociable.slug)
        return display_message_or_code(request, sociable)
    except ObjectDoesNotExist:
        context = {'search_code': search_code}
        return render(request, 'sociablecreating/sociable_not_found.html', context)


def display_message_or_code(request, sociable: Sociable):
    '''Given a sociable,
    displays the first unread message
    or displays the sociable detail page if there are no unread messages'''
    lst_logmessage = LogMessage.objects.filter(sociable=sociable, is_read=False)
    if lst_logmessage:
        context = {'sociable': sociable, 'logmessage': lst_logmessage[0]}
        return render(request, 'sociablecreating/message.html', context=context)
    else:
        return redirect('sociable', slug=sociable.slug)


def display_code_after_message_is_read(request, pk):
    '''Given the visitor clicks gelezen,
    update the message to read and display code'''
    logmessage = LogMessage.objects.get(id=pk)
    logmessage.is_read = True
    logmessage.save()
    return redirect('sociable', slug=logmessage.sociable)


def get_sociables_for_dashboard(user: User):
    '''Given a user,
    returns all the sociables
        - they participated in as author
        - and they own without a logmessage of themselves
    '''
    def logmessage_date_created(sociable):
        return sociable.logmessage_set.all()[0].date_created

    list_sociable = get_sociables_user_participated_as_author(user)
    list_sociable.extend(user.sociable_set.filter(logmessage__isnull=False))
    list_sociable = list(set(list_sociable))

    list_sociable.sort(reverse=True, key=logmessage_date_created)
    return list_sociable


def get_sociables_user_participated_as_author(user: User):
    '''Given a user, get all sociables that the user has written a logmessage in'''
    list_key_sociable_of_logmessage = user.logmessage_set.all().values_list('sociable', flat=True)
    return list(Sociable.objects.filter(pk__in=list_key_sociable_of_logmessage))


@login_required(login_url='login')
def create_sociable(request):
    '''Creates a sociable and redirects to it's detail page'''
    slug = get_random_string(8, allowed_chars=string.ascii_lowercase+string.digits)
    sociable = Sociable(owner=request.user, slug=slug)
    sociable.save()
    return redirect(reverse('sociable', args=[sociable.slug]))


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


class SociableDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model         = Sociable
    success_url   = reverse_lazy('dashboard_sociable')
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
