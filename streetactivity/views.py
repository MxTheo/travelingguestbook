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
    StreetActivityPhotoForm,
)
from .models import Reflection, StreetActivity, StreetActivityPhoto
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

    def get_context_data(self, **kwargs):
        """Extend context data with reflection and choose random photo"""
        context = super().get_context_data(**kwargs)
        context = self.add_reflection_context_data(activity=self.object, context=context)
        context["photo"] = self.get_random_photo(activity=self.object)
        return context

    def add_reflection_context_data(self, activity, context):
        '''Extend context data with reflection statistics'''
        reflections = activity.reflections.all()
        reflections_count = reflections.count()

        context["reflections_count"] = reflections_count
        context["recent_reflections"] = reflections[:3]
        context["reflections_remaining"] = max(0, reflections_count - 3)

        return context

    def get_random_photo(self, activity):
        """Given an activity,
        get a random photo associated with that activity"""
        return activity.photos.annotate(random=Random()).order_by('random').first()

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
    activity: StreetActivity

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
            "reflection-list-streetactivity",
            kwargs={"pk": self.object.activity.pk}
        )

class ReflectionViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Reflection"""

    queryset = Reflection.objects.all()
    serializer_class = ReflectionSerializer

class StreetActivityPhotoCreateView(CreateView):
    """
    View for uploading a photo for a StreetActivity.
    Uses the StreetActivityPhotoForm for validation and saving.
    """
    model = StreetActivityPhoto
    form_class = StreetActivityPhotoForm

    def form_valid(self, form):
        """
        Process the form when it is valid.
        Associates the uploaded photo with the current StreetActivity.
        """
        photo = form.save(commit=False)
        activity_id = self.kwargs.get('activity_id')
        photo.activity = get_object_or_404(StreetActivity, id=activity_id)
        photo.save()
        messages.success(self.request, "Je foto is succesvol geupload!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submissions.
        Display an error message to the user.
        """
        messages.error(self.request, "Er was een fout bij het uploaden van je foto. Controleer het bestand en probeer opnieuw.")
        return super().form_invalid(form)

    def get_success_url(self):
        """Use the activity id from the URL
          to redirect to the gallery after a successful upload"""
        activity_id = self.kwargs.get('activity_id')
        return reverse_lazy(
            "streetactivity-photo-list",
            kwargs={"activity_id": activity_id}
        )

class StreetActivityPhotoDeleteView(DeleteView):
    '''Delete view for streetactivity photo'''
    model = StreetActivityPhoto
    template_name = CONFIRM_DELETE_TEMPLATE

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.WARNING, "De foto is verwijderd."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "streetactivity-photo-list",
            kwargs={"activity_id": self.object.activity.pk}
        )

class StreetActivityPhotoListView(ListView):
    """View to list photos related to a specific street activity."""
    model = StreetActivityPhoto
    context_object_name = "photos"
    paginate_by = 10

    def get_queryset(self):
        """Filter photos by street activity ID from URL."""
        activity_id = self.kwargs["activity_id"]
        return StreetActivityPhoto.objects.filter(activity_id=activity_id)

    def get_context_data(self, **kwargs):
        """Add street activity to context for header."""
        context = super().get_context_data(**kwargs)
        context["activity"] = get_object_or_404(
            StreetActivity, pk=self.kwargs["activity_id"]
        )
        return context

class StreetActivityPhotoDetailView(DetailView):
    """View to display details of a single street activity photo."""
    model = StreetActivityPhoto
    context_object_name = "photo"
    
    def get_context_data(self, **kwargs):
        """Extend context data with word statistics for charts"""
        context = super().get_context_data(**kwargs)
        activity = self.object.activity
        context['activity'] = activity

        return context