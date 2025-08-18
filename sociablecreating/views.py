from django.utils import timezone
from django.forms import BaseModelForm
from django.shortcuts import redirect, render
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from sociablecreating.forms import LogMessageForm
from .models import LogMessage, Sociable


def home(request):
    """Renders the homepage of the sociablecreating app"""
    return render(request, "sociablecreating/index.html")

def create_sociable(request):
    """Creates a sociable and redirects to it's detail page"""
    slug = get_random_string(7, allowed_chars='abcdefghjklmnpqrstuvwxyz23456789')
    sociable = Sociable(slug=slug)
    sociable.save()
    return redirect(reverse("sociable", args=[sociable.slug]))

class LogMessageCreate(generic.edit.CreateView):
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
        return super(LogMessageCreate, self).form_valid(form)

    def set_sociable(self, form):
        """Given the log message and the sociable slug from the context,
        sets the sociable relationship for the created log message"""
        slug = super().get_context_data()["view"].kwargs["slug"]
        sociable = Sociable.objects.get(slug=slug)
        form.instance.sociable = sociable

class LogMessageDelete(generic.edit.DeleteView):
    """Generic editing view to delete LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = LogMessage
    template_name = "admin/confirm_delete.html"

    def get_success_url(self):
        logmessage = self.get_object()
        sociable = logmessage.sociable
        return reverse("sociable", kwargs={"slug": sociable.slug})


class LogMessageUpdate(generic.edit.UpdateView):
    """Generic editing view to update LogMessage:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = LogMessage
    form_class = LogMessageForm

    def form_valid(self, form: BaseModelForm):
        """Set the date changed to today"""
        form.instance.date_changed = timezone.now()
        return super(LogMessageUpdate, self).form_valid(form)

class SociableDelete(generic.edit.DeleteView):
    """Generic editing view to delete Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/"""

    model = Sociable
    success_url = reverse_lazy("chat")
    template_name = "admin/confirm_delete.html"


class SociableDetail(generic.DetailView):
    """Generic display view to show detailpage of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model = Sociable

class SociableList(generic.ListView):
    """Generic display view to show an overview of Sociable:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/"""

    model = Sociable
