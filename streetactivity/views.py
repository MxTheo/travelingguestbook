from django.contrib import messages
from django.db.models.functions import Random
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from rest_framework import viewsets

from .forms import (
    ReflectionForm,
    StreetActivityForm,
)
from .models import Reflection, StreetActivity
from .serializers import ReflectionSerializer, StreetActivitySerializer

CONFIRM_DELETE_TEMPLATE = "admin/confirm_delete.html"

class StreetActivityListView(ListView):
    """View to list all street activities with filtering options."""

    model = StreetActivity
    context_object_name = "activities"
    paginate_by = 10


class StreetActivityDetailView(DetailView):
    """View to display details of a single street activity."""
    model = StreetActivity
    context_object_name = "activity"

class StreetActivityCreateView(CreateView):
    """View to create a new street activity."""

    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy("streetactivity-detail", kwargs={"pk": self.object.pk})


class StreetActivityUpdateView(UpdateView):
    """View to update an existing street activity."""

    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy("streetactivity-detail", kwargs={"pk": self.object.pk})


class StreetActivityDeleteView(DeleteView):
    """View to delete a street activity."""

    model = StreetActivity
    template_name = CONFIRM_DELETE_TEMPLATE
    success_url = reverse_lazy("streetactivity-list")


class StreetActivityViewSet(viewsets.ModelViewSet):
    """API endpoint that allows streetactivity to be viewed or edited"""

    queryset = StreetActivity.objects.all()
    serializer_class = StreetActivitySerializer


class ReflectionListView(ListView):
    """View to list all reflections."""

    model = Reflection
    context_object_name = "reflections"
    paginate_by = 10

class ReflectionDetailView(DetailView):
    """View to display details of a single reflection."""

    model = Reflection
    context_object_name = "reflection"


class ReflectionCreateView(CreateView):
    """Create view for a single reflection"""

    model = Reflection
    form_class = ReflectionForm

    def form_valid(self, form):
        """Add success message when the form is valid."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            """Bedankt voor het delen van jouw reflectie! 
                Dit helpt anderen de activiteit te begrijpen.""",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "reflection-list"
        )


class ReflectionDeleteView(DeleteView):
    """View to delete an reflection"""

    model = Reflection
    template_name = CONFIRM_DELETE_TEMPLATE

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.WARNING, "De reflectie is verwijderd."
        )
        return super().form_valid(form)

    def get_success_url(self):
        """Go to all reflections"""
        return reverse_lazy("reflection-list")

class ReflectionViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Reflection"""

    queryset = Reflection.objects.all()
    serializer_class = ReflectionSerializer


class ReflectionPhotoListView(ListView):
    """View to list photos from reflections."""
    model = Reflection
    context_object_name = "reflections_with_photo"
    paginate_by = 10
    template_name = "streetactivity/reflectionphoto_list.html"

    def get_queryset(self):
        """Filter reflections with photos (media_url not null or empty)"""
        return Reflection.objects.filter(media_url__isnull=False).exclude(media_url='')
