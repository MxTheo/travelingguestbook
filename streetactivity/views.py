from typing import Optional
from rest_framework import viewsets
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .serializers import StreetActivitySerializer, ReflectionSerializer
from .models import StreetActivity, Reflection
from .forms import (
    ReflectionForm,
    StreetActivityForm,
)

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

    def get_context_data(self, **kwargs):
        """Extend context data with word statistics for charts"""
        context = super().get_context_data(**kwargs)
        activity = self.object

        reflections = activity.reflections.all()
        reflections_count = reflections.count()

        context["reflections_count"] = reflections_count
        context["recent_reflections"] = reflections[:3]
        context["reflections_remaining"] = max(0, reflections_count - 3)

        return context

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


class ReflectionListViewStreetActivity(ReflectionListView):
    """View to list reflections related to a specific street activity."""

    def get_queryset(self):
        """Filter reflections by street activity ID from URL."""
        activity_id = self.kwargs["pk"]
        return Reflection.objects.filter(activity_id=activity_id)

    def get_context_data(self, **kwargs):
        """Add street activity to context for header."""
        context = super().get_context_data(**kwargs)
        context["street_activity"] = get_object_or_404(
            StreetActivity, pk=self.kwargs["pk"]
        )
        return context


class ReflectionDetailView(DetailView):
    """View to display details of a single reflection."""

    model = Reflection
    context_object_name = "reflection"


class ReflectionCreateView(CreateView):
    """Create view for a single reflection"""

    model = Reflection
    form_class = ReflectionForm
    activity: Optional[StreetActivity] = None

    def dispatch(self, request, *args, **kwargs):
        """Determine activity ID from URL parameters."""
        self.activity = get_object_or_404(StreetActivity, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Set initial values"""
        initial = super().get_initial()
        initial["activity"] = self.activity
        return initial

    def get_context_data(self, **kwargs):
        """Extend context data with activity"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.activity
        return context

    def form_valid(self, form):
        """Set the activity for the word"""
        form.instance.activity = self.activity

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Bedankt voor het delen van jouw reflectie! "
            "Dit helpt anderen dit spel te begrijpen.",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "reflection-list-streetactivity",
            kwargs={"pk": self.object.activity.pk},  # type: ignore[reportOptionalMemberAccess]
        )

class ReflectionUpdateView(UpdateView):
    """View to update an reflection"""

    model = Reflection
    form_class = ReflectionForm

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.object.activity
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.WARNING, "De reflectie is aangepast.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "reflection-list-streetactivity", kwargs={"pk": self.object.activity.pk}
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
        return reverse_lazy(
            "reflection-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )

class ReflectionViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Reflection"""

    queryset = Reflection.objects.all()
    serializer_class = ReflectionSerializer
