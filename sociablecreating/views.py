from django.utils import timezone
from django.forms import BaseModelForm
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
    """Renders the homepage of the sociablecreating app"""
    return render(request, "sociablecreating/index.html")


def show_unread_message(request, slug):
    """Given the sociable,
    show the first unread message that are not of the author
    No unread message, then show sociable"""
    sociable       = Sociable.objects.get(slug=slug)
    lst_logmessage = LogMessage.objects.filter(sociable=sociable, is_read=False)
    if request.user.is_authenticated:
        lst_logmessage = lst_logmessage.exclude(author=request.user)
    if len(lst_logmessage) > 0:
        context = {"sociable": sociable, "logmessage": lst_logmessage[0]}
        return render(request, 'sociablecreating/unread_message.html', context)
    return redirect('detail-sociable', slug=sociable.slug)


def search_sociable(request):
    """Given a search-code entered by the user,
    redirect the user to the sociable associated or let the user knows the sociable is not found"""
    search_code = request.GET["search-code"].lower()
    try:
        return show_unread_message(request, search_code)
    except ObjectDoesNotExist:
        context = {"search_code": search_code}
        return render(request, "sociablecreating/sociable_not_found.html", context)


def search_sociable_by_number(request):
    """When the user enters the number on the card,
    redirect the user to the sociable"""
    number = request.GET["number"]
    owner  = request.GET["owner"]
    sociable = Sociable.objects.get(number=number, owner=owner)
    return show_unread_message(request, sociable.slug)

def display_sociable_after_message_is_read(request, pk):
    """Given the visitor clicks gelezen,
    update the message to read and display code"""
    logmessage = LogMessage.objects.get(id=pk)
    logmessage.is_read = True
    logmessage.save()
    return redirect("sociable", slug=logmessage.sociable)


def get_sociables_for_dashboard(user: User):
    """Given a user,
    returns all the sociables
        - they participated in as author
        - and they own without a logmessage of themselves
    """
    def logmessage_date_created(sociable: Sociable):
        return sociable.logmessage_set.all()[0].date_created

    list_sociable = get_sociables_user_participated_as_author(user)
    list_sociable.extend(user.sociable_set.filter(logmessage__isnull=False))
    list_sociable = list(set(list_sociable))

    list_sociable.sort(reverse=True, key=logmessage_date_created)
    return list_sociable


def get_sociables_user_participated_as_author(user: User):
    """Given a user, get all sociables that the user has written a logmessage in"""
    list_key_sociable_of_logmessage = user.logmessage_set.all().values_list(
        "sociable", flat=True
    )
    return list(Sociable.objects.filter(pk__in=list_key_sociable_of_logmessage))


@login_required(login_url="login")
def create_sociable(request):
    """Creates a sociable and redirects to it's detail page"""
    slug = get_random_string(7, allowed_chars='abcdefghjklmnpqrstuvwxyz23456789')
    number = calc_number_for_sociable(request)
    sociable = Sociable(owner=request.user, slug=slug, number=number)
    sociable.save()
    return redirect(reverse("sociable", args=[sociable.slug]))

def calc_number_for_sociable(request):
    """The number of the sociable is the n'th sociable of the user
    Calculates the number for the sociable"""
    list_sociable = Sociable.objects.filter(owner=request.user)
    return list_sociable[0].number + 1 if list_sociable else 1

class LogMessageCreate(generic.edit.CreateView, LoginRequiredMixin):
    """Generic editing view to create LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    form_class = LogMessageForm
    model = LogMessage

    def get_initial(self):
        """If logged in, the username is entered as initial value of name"""
        initial = super().get_initial()
        user = self.request.user
        if not user.is_anonymous:
            initial["name"] = user.username
        return initial

    def form_valid(self, form):
        """After the form is valid, set the relationships"""
        self.set_sociable(form)
        self.set_author(form)
        self.update_xp_and_lvl()
        return super(LogMessageCreate, self).form_valid(form)

    def set_author(self, form):
        """Given the logmessage and the user,
        sets the user as the author, if user is logged in"""
        user = self.request.user
        if not user.is_anonymous:
            form.instance.author = user

    def set_sociable(self, form):
        """Given the log message and the sociable slug from the context,
        sets the sociable relationship for the created log message"""
        slug = super().get_context_data()["view"].kwargs["slug"]
        sociable = Sociable.objects.get(slug=slug)
        form.instance.sociable = sociable

    def update_xp_and_lvl(self):
        """When creating a logmessage,
        update the xp values and lvl when needed
        xp_needed is lvl ^ 1.2
        """
        user = self.request.user
        if not user.is_anonymous:
            profile = Profile.objects.get(user=user)
            profile.xp += 1
            if profile.xp == profile.xp_next_lvl:
                profile.lvl += 1
                profile.xp_start_lvl = profile.xp_next_lvl
                profile.xp_next_lvl += round(profile.lvl**1.2)
            profile.save()


class LogMessageDelete(UserPassesTestMixin, generic.edit.DeleteView):
    """Generic editing view to delete LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = LogMessage
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        """Only the owner may delete logmessages from their sociable"""
        logmessage = self.get_object()
        sociable = logmessage.sociable
        return self.request.user.pk == sociable.owner_id

    def get_success_url(self):
        logmessage = self.get_object()
        sociable = logmessage.sociable
        return reverse("sociable", kwargs={"slug": sociable.slug})


class LogMessageUpdate(
    LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView
):
    """Generic editing view to update LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = LogMessage
    form_class = LogMessageForm

    def test_func(self) -> bool | None:
        """Both the owner of the sociable and the author may update the sociable"""
        logmessage = self.get_object()
        sociable = logmessage.sociable
        user_id = self.request.user.pk
        return logmessage.author_id == user_id or sociable.owner_id == user_id

    def form_valid(self, form: BaseModelForm):
        """Set the date changed to today"""
        form.instance.date_changed = timezone.now()
        return super(LogMessageUpdate, self).form_valid(form)


class SociableDelete(UserPassesTestMixin, generic.edit.DeleteView):
    """Generic editing view to delete Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = Sociable
    success_url = reverse_lazy("dashboard_sociable")
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        sociable = Sociable.objects.get(slug=self.kwargs["slug"])
        return self.request.user == sociable.owner


class SociableDetail(generic.DetailView):
    """Generic display view to show detailpage of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model = Sociable

class SociableList(generic.ListView):
    """Generic display view to show an overview of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model = Sociable
