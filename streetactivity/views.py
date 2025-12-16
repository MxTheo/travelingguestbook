from collections import Counter
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from rest_framework import viewsets
from usermanagement.views import add_xp, update_lvl, calc_xp_percentage
from .serializers import StreetActivitySerializer, MomentSerializer
from .models import StreetActivity, Moment, Experience
from .forms import (
    MomentForm,
    StreetActivityForm,
    ExperienceForm,
)

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
        """Extend context data with moment statistics for charts"""
        context = super().get_context_data(**kwargs)
        activity = self.object

        moments = activity.moments.all()
        moments_count = moments.count()

        context["moments_count"] = moments_count
        context["practitioner_count"] = moments.filter(
            from_practitioner=True
        ).count()
        context["passerby_count"] = moments.filter(from_practitioner=False).count()
        context["recent_moments"] = moments[:3]
        context["moments_remaining"] = max(0, moments_count - 3)

        def get_chart_data(queryset):
            confidence_level_counts = queryset.values("confidence_level").annotate(
                count=Count("confidence_level"))
            data = {"pioneer": 0, "intermediate": 0, "climax": 0}
            for item in confidence_level_counts:
                data[item["confidence_level"]] = item["count"]
            return data

        context["chart_data_everyone"] = get_chart_data(moments)
        context["chart_data_practitioners"] = get_chart_data(
            moments.filter(from_practitioner=True)
        )
        context["chart_data_passersby"] = get_chart_data(
            moments.filter(from_practitioner=False)
        )

        context["word_counts"] = self.analyse_keywords(moments)

        return context

    def analyse_keywords(self, moments):
        """Given the moments of the streetactivity,
        count every keyword and return the 10 most common keywords in a list tuple"""
        all_keywords = []
        for moment in moments:
            if moment.keywords:
                words = [w.strip().lower() for w in moment.keywords.split(',')]
                all_keywords.extend(words)
        return Counter(all_keywords).most_common(10)

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
    template_name = "admin/confirm_delete.html"
    success_url = reverse_lazy("streetactivity-list")

class StreetActivityViewSet(viewsets.ModelViewSet):
    """API endpoint that allows streetactivity to be viewed or edited"""
    queryset = StreetActivity.objects.all()
    serializer_class = StreetActivitySerializer


class MomentListView(ListView):
    """View to list all moments."""
    model = Moment
    context_object_name = "moments"
    paginate_by = 10

class MomentListViewStreetActivity(MomentListView):
    """View to list moments related to a specific street activity."""

    def get_queryset(self):
        """Filter moments by street activity ID from URL."""
        activity_id = self.kwargs["pk"]
        return Moment.objects.filter(activity_id=activity_id)

    def get_context_data(self, **kwargs):
        """Add street activity to context for header."""
        context = super().get_context_data(**kwargs)
        context["street_activity"] = StreetActivity.objects.get(pk=self.kwargs["pk"])
        return context

class MomentDetailView(DetailView):
    """View to display details of a single moment."""

    model = Moment
    context_object_name = "moment"

class MomentCreateView(CreateView):
    """Base view to create a new moment."""

    model = Moment
    form_class = MomentForm

    def get_initial(self):
        """Set initial values including from_practitioner"""
        initial = super().get_initial()
        # Bepaal of het een practitioner of passerby is op basis van de URL
        initial["from_practitioner"] = "beoefenaar" in self.request.path
        return initial

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        activity_id = self.kwargs["pk"]
        context["activity"] = get_object_or_404(StreetActivity, pk=activity_id)
        return context

    def form_valid(self, form):
        activity_id = self.kwargs["pk"]
        form.instance.activity_id = activity_id

        messages.add_message(self.request, messages.SUCCESS,
                             "Bedankt voor het delen van jouw moment! " \
                             "Dit helpt anderen deze activiteit te begrijpen. ")

        if "beoefenaar" in self.request.path:
            form.instance.from_practitioner = True
        else:
            form.instance.from_practitioner = False
        
        if not self.request.user.is_anonymous:
            profile = self.request.user.profile
            add_xp(profile, form.instance.confidence_level)
            update_lvl(profile)
            calc_xp_percentage(profile)
            profile.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )

class MomentUpdateView(UpdateView):
    """View to update an moment"""
    model = Moment
    form_class = MomentForm

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.object.activity
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.WARNING, "Het moment is aangepast.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )

class MomentDeleteView(DeleteView):
    """View to delete an moment"""
    model = Moment
    template_name = "admin/confirm_delete.html"

    def form_valid(self, form):
        messages.add_message(self.request, messages.WARNING, "Het moment is verwijderd.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )

class MomentViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Moment"""
    queryset = Moment.objects.all()
    serializer_class = MomentSerializer

class ExperienceCreateView(CreateView):
    """View to create a new experience."""

    model = Experience
    form_class = ExperienceForm

    def form_valid(self, form):
        """Sets the user"""
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect naar een moment toevoegen voor deze ervaring
        # PLACEHOLDER: later koppelen aan create-moment-from-practitioner
        return reverse_lazy('create-moment-from-practitioner', 
                          kwargs={'pk': 0})  # placeholder


class ExperienceDetailView(DetailView):
    """Detailview of experience with its related moments"""
    model = Experience
    context_object_name = "experience"

    def get_context_data(self, **kwargs):
        """Extend context data with related moments"""
        context = super().get_context_data(**kwargs)
        experience = self.object
        context["moments"] = experience.moments.all()
        return context

class CompleteExperienceView(UpdateView):
    """View to mark an experience as complete."""
    model = Experience
    fields = []

    def form_valid(self, form):
        form.instance.is_complete = True
        messages.add_message(self.request, messages.SUCCESS,
                             "Je ervaring is gemarkeerd als voltooid!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("experience-detail", kwargs={"pk": self.object.pk})
    
class ExperienceViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Experience"""
    queryset = Experience.objects.all()
    serializer_class = ExperienceForm