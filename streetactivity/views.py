from typing import Optional
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from rest_framework import viewsets
from usermanagement.views import add_xp, update_lvl, calc_xp_percentage
from .serializers import StreetActivitySerializer, MomentSerializer
from .models import StreetActivity, Moment
from .forms import (
    MomentForm,
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
        """Extend context data with moment statistics for charts"""
        context = super().get_context_data(**kwargs)
        activity = self.object

        moments = activity.moments.all()
        moments_count = moments.count()

        context["moments_count"] = moments_count
        context["recent_moments"] = moments[:3]
        context["moments_remaining"] = max(0, moments_count - 3)

        return context

class StreetActivityCreateView(CreateView, LoginRequiredMixin):
    """View to create a new street activity."""

    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy("streetactivity-detail", kwargs={"pk": self.object.pk})


class StreetActivityUpdateView(UpdateView, LoginRequiredMixin):
    """View to update an existing street activity."""

    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy("streetactivity-detail", kwargs={"pk": self.object.pk})


class StreetActivityDeleteView(DeleteView, LoginRequiredMixin):
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
        context["street_activity"] = get_object_or_404(
            StreetActivity, pk=self.kwargs["pk"]
        )
        return context


class MomentDetailView(DetailView):
    """View to display details of a single moment."""

    model = Moment
    context_object_name = "moment"


class MomentCreateView(CreateView, LoginRequiredMixin):
    """Create view for a single moment"""

    model = Moment
    form_class = MomentForm
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
        """Set the activity and user for the moment, then process XP and level updates."""
        form.instance.activity = self.activity
        form.instance.user = self.request.user
        process_xp_and_level(self.request)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Bedankt voor het delen van jouw woord! "
            "Dit helpt anderen deze activiteit te begrijpen.",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity",
            kwargs={"pk": self.object.activity.pk},  # type: ignore[reportOptionalMemberAccess]
        )


def process_xp_and_level(request):
    """Given a request,
    process XP and level update for the user profile."""
    profile = request.user.profile  # type: ignore[reportAttributeAccessIssue]
    add_xp(profile)
    update_lvl(profile)
    calc_xp_percentage(profile)
    profile.save()

class MomentUpdateView(UpdateView, LoginRequiredMixin):
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


class MomentDeleteView(DeleteView, LoginRequiredMixin):
    """View to delete an moment"""

    model = Moment
    template_name = CONFIRM_DELETE_TEMPLATE

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.WARNING, "Het moment is verwijderd."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )


class MomentViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Moment"""

    queryset = Moment.objects.all()
    serializer_class = MomentSerializer
