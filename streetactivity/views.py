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
from .serializers import StreetActivitySerializer
from .models import StreetActivity, Experience
from .forms import (
    ExperienceForm,
    StreetActivityForm,
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
        """Extend context data with experience statistics for charts"""
        context = super().get_context_data(**kwargs)
        activity = self.object

        experiences = activity.experiences.all()
        experiences_count = experiences.count()

        context["experiences_count"] = experiences_count
        context["practitioner_count"] = experiences.filter(
            from_practitioner=True
        ).count()
        context["passerby_count"] = experiences.filter(from_practitioner=False).count()
        context["recent_experiences"] = experiences[:3]
        context["experiences_remaining"] = max(0, experiences_count - 3)

        def get_chart_data(queryset):
            confidence_level_counts = queryset.values("confidence_level").annotate(count=Count("confidence_level"))
            data = {"pioneer": 0, "intermediate": 0, "climax": 0}
            for item in confidence_level_counts:
                data[item["confidence_level"]] = item["count"]
            return data

        context["chart_data_everyone"] = get_chart_data(experiences)
        context["chart_data_practitioners"] = get_chart_data(
            experiences.filter(from_practitioner=True)
        )
        context["chart_data_passersby"] = get_chart_data(
            experiences.filter(from_practitioner=False)
        )

        context["word_counts"] = self.analyse_keywords(experiences)

        return context

    def analyse_keywords(self, experiences):
        """Given the experiences of the streetactivity,
        count every keyword and return the 10 most common keywords in a list tuple"""
        all_keywords = []
        for experience in experiences:
            if experience.keywords:
                words = [w.strip().lower() for w in experience.keywords.split(',')]
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


class ExperienceListView(ListView):
    """View to list all experiences."""

    model = Experience
    context_object_name = "experiences"
    paginate_by = 10


class ExperienceListViewStreetActivity(ExperienceListView):
    """View to list experiences related to a specific street activity."""

    def get_queryset(self):
        """Filter experiences by street activity ID from URL."""
        activity_id = self.kwargs["pk"]
        return Experience.objects.filter(activity_id=activity_id)

    def get_context_data(self, **kwargs):
        """Add street activity to context for header."""
        context = super().get_context_data(**kwargs)
        context["street_activity"] = StreetActivity.objects.get(pk=self.kwargs["pk"])
        return context


class ExperienceDetailView(DetailView):
    """View to display details of a single experience."""

    model = Experience
    context_object_name = "experience"


class ExperienceCreateView(CreateView):
    """Base view to create a new experience."""

    model = Experience
    form_class = ExperienceForm

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
                             "Dit helpt anderen deze activiteit te begrijpen. " \
                             "Zie ook 'Alle momenten'")

        if "beoefenaar" in self.request.path:
            form.instance.from_practitioner = True
        else:
            form.instance.from_practitioner = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "streetactivity-detail", kwargs={"pk": self.object.activity.pk}
        )
