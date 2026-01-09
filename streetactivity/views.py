from collections import Counter
import json
from typing import Optional
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from usermanagement.views import add_xp, update_lvl, calc_xp_percentage
from .serializers import StreetActivitySerializer, MomentSerializer
from .models import StreetActivity, Moment, Experience, ConfidenceLevel
from .forms import (
    MomentForm,
    StreetActivityForm,
    ExperienceForm,
    AddMomentToExperienceForm,
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
            data = {"onzeker": 0, "tussenin": 0, "zelfverzekerd": 0}

            confidence_mapping = {
                ConfidenceLevel.ONZEKER: "onzeker",
                ConfidenceLevel.TUSSENIN: "tussenin",
                ConfidenceLevel.ZELFVERZEKERD: "zelfverzekerd"
            }
            for item in confidence_level_counts:
                confidence_value = item["confidence_level"]
                if confidence_value in confidence_mapping:
                    key = confidence_mapping[confidence_value]
                    data[key] = item["count"]
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
        return reverse_lazy("streetactivity-detail",
                            kwargs={"pk": self.object.pk})  # type: ignore[reportOptionalMemberAccess]

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
    activity: Optional[StreetActivity] = None

    def dispatch(self, request, *args, **kwargs):
        """Determine activity ID from URL parameters."""
        if "pk" in self.kwargs:
            self.activity = get_object_or_404(StreetActivity, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Set initial values including from_practitioner"""
        initial = super().get_initial()
        if "voorbijganger" in self.request.path:
            initial["from_practitioner"] = False
        else:
            initial["from_practitioner"] = True

        if "pk" in self.kwargs:
            initial["activity"] = self.activity
        return initial

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        if "pk" in self.kwargs:
            context["activity"] = self.activity
        context['ConfidenceLevel'] = ConfidenceLevel
        return context

    def form_valid(self, form):
        if "pk" in self.kwargs:
            form.instance.activity = self.activity

        messages.add_message(self.request, messages.SUCCESS,
                             "Bedankt voor het delen van jouw moment! " \
                             "Dit helpt anderen deze activiteit te begrijpen. ")

        if "voorbijganger" in self.request.path:
            form.instance.from_practitioner = False
        else:
            form.instance.from_practitioner = True

        if not self.request.user.is_anonymous:
            profile = self.request.user.profile  # type: ignore[reportAttributeAccessIssue]
            add_xp(profile, form.instance.confidence_level)
            update_lvl(profile)
            calc_xp_percentage(profile)
            profile.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity",
            kwargs={"pk": self.object.activity.pk}  # type: ignore[reportOptionalMemberAccess]
        )

class AddMomentToExperienceView(MomentCreateView, LoginRequiredMixin):
    """View to add a moment to an experience."""

    form_class = AddMomentToExperienceForm
    context_object_name = "experience"
    experience_id: Optional[int] = None

    def dispatch(self, request, *args, **kwargs):
        """Determine experience ID from URL parameters. If not present, create a new experience."""
        self.experience_id = self.kwargs.get("experience_id", None)
        if not self.experience_id:
            messages.info(self.request,
                     """Voeg nu je eerste moment toe aan de ervaring. 
                     Hoe zelfverzekerd voelde jij je toen je begon?""")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Extend context data with experience"""
        context = super().get_context_data(**kwargs)
        context['from_experience'] = True
        return context

    def form_valid(self, form):
        """Link the moment to the experience"""
        if self.experience_id:
            experience = get_object_or_404(Experience, pk=self.experience_id)
        else:
            experience = Experience.objects.create(user=self.request.user)
            self.experience_id = experience.id
        form.instance.experience = experience
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the experience form after adding moment"""
        return reverse_lazy('experience-detail',
                            kwargs={'pk': self.experience_id})

class MomentUpdateView(UpdateView):
    """View to update an moment"""
    model = Moment
    form_class = MomentForm

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.object.activity
        context['ConfidenceLevel'] = ConfidenceLevel
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
    template_name = CONFIRM_DELETE_TEMPLATE

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

class StartExperienceView(LoginRequiredMixin, TemplateView):
    """Navigates to the start experience page"""
    template_name = "streetactivity/start_experience.html"

class ExperienceDetailView(DetailView):
    """Detailview of experience with its related moments"""
    model = Experience
    context_object_name = "experience"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_moment_data_to_context(context)
        return context

    def add_moment_data_to_context(self, context):
        """Adds a list of moments and moment data in JSON format to context"""
        moments = list(self.object.moments.order_by('date_created').select_related('activity'))
        moment_data = []
        for moment in moments:
            moment_data.append({
                'id': moment.id,
                'activity': {
                    'name': moment.activity.name,
                    'id': moment.activity.id
                },
                'confidence_level': moment.confidence_level,
                'report': moment.report,
                'report_snippet': moment.report[:25] + '...' 
                if moment.report and len(moment.report) > 25 else moment.report,
                'order': moment.order,
                'from_practitioner': moment.from_practitioner
            })

        context["moments"] = moments
        context['moments_json'] = json.dumps(moment_data)
        return context

class ExperienceDeleteView(DeleteView):
    """View to delete an experience"""
    model = Experience
    template_name = CONFIRM_DELETE_TEMPLATE
    success_url = reverse_lazy("user")

    def get_success_url(self):
        return reverse_lazy(
            "user", kwargs={"username": self.object.user.username}
        )

class ExperienceViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Experience"""
    queryset = Experience.objects.all()
    serializer_class = ExperienceForm
