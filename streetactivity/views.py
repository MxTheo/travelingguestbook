import json
from typing import Optional
from django.db import transaction
from django.contrib import messages
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    FormView,
)
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from usermanagement.views import add_xp, update_lvl, calc_xp_percentage
from .serializers import StreetActivitySerializer, MomentSerializer, ExperienceSerializer
from .models import StreetActivity, Moment, Experience, ConfidenceLevel
from .forms import (
    MomentForm,
    StreetActivityForm,
    ExperienceForm,
    AddMomentForm,
)
from .utils.session_helpers import setup_session_for_cancel, clear_session_data

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
        context["practitioner_count"] = moments.filter(from_practitioner=True).count()
        context["passerby_count"] = moments.filter(from_practitioner=False).count()
        context["recent_moments"] = moments[:3]
        context["moments_remaining"] = max(0, moments_count - 3)

        def get_chart_data(queryset):
            confidence_level_counts = queryset.values("confidence_level").annotate(
                count=Count("confidence_level")
            )
            data = {"onzeker": 0, "tussenin": 0, "zelfverzekerd": 0}

            confidence_mapping = {
                ConfidenceLevel.ONZEKER: "onzeker",
                ConfidenceLevel.TUSSENIN: "tussenin",
                ConfidenceLevel.ZELFVERZEKERD: "zelfverzekerd",
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


class MomentCreateView(CreateView):
    """Create view for a single moment"""

    model = Moment
    form_class = MomentForm
    activity: Optional[StreetActivity] = None

    def dispatch(self, request, *args, **kwargs):
        """Determine activity ID from URL parameters."""
        self.activity = get_object_or_404(StreetActivity, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Set initial values including from_practitioner"""
        initial = super().get_initial()
        if "voorbijganger" in self.request.path:
            initial["from_practitioner"] = False
        else:
            initial["from_practitioner"] = True

        initial["activity"] = self.activity
        return initial

    def get_context_data(self, **kwargs):
        """Extend context data with activity and ConfidenceLevel options"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.activity
        context["ConfidenceLevel"] = ConfidenceLevel
        return context

    def form_valid(self, form):
        form.instance.activity = self.activity
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Bedankt voor het delen van jouw moment! "
            "Dit helpt anderen deze activiteit te begrijpen.",
        )

        if "voorbijganger" in self.request.path:
            form.instance.from_practitioner = False
        else:
            form.instance.from_practitioner = True

        if not self.request.user.is_anonymous:
            process_xp_and_level(self.request, form.instance.confidence_level)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "moment-list-streetactivity",
            kwargs={"pk": self.object.activity.pk},  # type: ignore[reportOptionalMemberAccess]
        )


def process_xp_and_level(request, confidence_level):
    """Given a request and confidence level,
    process XP and level update for the user profile."""
    profile = request.user.profile  # type: ignore[reportAttributeAccessIssue]
    add_xp(profile, int(confidence_level))
    update_lvl(profile)
    calc_xp_percentage(profile)
    profile.save()


class AddMomentToExperienceView(FormView, LoginRequiredMixin):
    """View to add a moment to an experience."""

    model = Moment
    form_class = AddMomentForm
    template_name = "streetactivity/moment_form.html"
    context_object_name = "experience"
    experience_id: Optional[str] = None

    def dispatch(self, request, *args, **kwargs):
        """Determine experience ID from URL parameters. If not present, create a new experience."""
        self.experience_id = self.kwargs.get("experience_id", None)
        if self.experience_id:
            request.session["experience_id"] = str(self.experience_id)
        request.session["from_experience"] = True
        setup_session_for_cancel(request, self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Set initial values from session moment_data if available"""
        initial = super().get_initial()
        moment_data = self.request.session.get("moment_data")
        if moment_data:
            initial.update(moment_data)
        return initial

    def get_context_data(self, **kwargs):
        """Extend context data with experience"""
        context = super().get_context_data(**kwargs)
        context["selected_activity"] = self.retrieve_selected_activity()
        if not self.experience_id:
            context["show_first_moment_message"] = True
        context["ConfidenceLevel"] = ConfidenceLevel
        return context

    def retrieve_selected_activity(self):
        """Retrieve selected activity from session if available
        or from last moment of experience
        , else none"""
        selected_activity_id = self.request.session.get("selected_activity_id")
        if selected_activity_id:
            return get_object_or_404(StreetActivity, id=selected_activity_id)
        if self.experience_id:
            experience = get_object_or_404(Experience, id=self.experience_id)
            last_moment = experience.moments.first()
            if last_moment:
                self.request.session["selected_activity_id"] = last_moment.activity.id
                return last_moment.activity
        return None

    def form_valid(self, form):
        """
        Save form data in session,
        then redirect to activity selection page
        """
        self.request.session["moment_data"] = form.cleaned_data
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the next step: 
            - assign activity to moment if user chose to save moment
            - select activity for moment if user chose to select activity
        """
        submit_action = self.request.POST.get("submit_action")
        if submit_action == "select_activity":
            return reverse("select-activity-for-moment")
        elif submit_action == "save_moment":
            return reverse("assign-activity-to-moment")
        return reverse("select-activity-for-moment")


class SelectActivityForMomentView(LoginRequiredMixin, ListView):
    """View to select street activity for a moment being created"""

    model = StreetActivity
    template_name = "streetactivity/select_activity_for_moment.html"
    context_object_name = "activities"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_activity_id = self.request.session.get("selected_activity_id")
        context["selected_activity_id"] = selected_activity_id
        context["back_url"] = self.create_back_url()
        return context

    def create_back_url(self):
        """Create a url to get back to depending if a experience_id is present"""
        experience_id = self.request.session.get("experience_id")
        if experience_id:
            return reverse("add-moment-to-experience", args=[experience_id])
        else:
            return reverse("add-first-moment-to-experience")

    def get(self, request, *args, **kwargs):
        """Handle GET request to preselect activity if activity_id is in GET params"""
        selected_activity = self.retrieve_activity(request)
        if selected_activity:
            request.session["selected_activity_id"] = selected_activity.id
        return super().get(request, *args, **kwargs)

    def retrieve_activity(self, request):
        """Retrieve activity based on GET parameter or session data.
        - activity_id: When the user clicks an activity in the template,
        the activity_id is saved in the url as ?activity_id={{ activity.id }}
        and retrieved from there
        - selected_activity_id: The preselection comes from the previously selected activity
        - If the user visits the page for the first time,
        then the first streetactivity is selected
        """

        activity_id = request.GET.get("activity_id")
        if activity_id:
            return get_object_or_404(StreetActivity, pk=activity_id)
        selected_activity_id = request.session.get("selected_activity_id")
        if selected_activity_id:
            return get_object_or_404(StreetActivity, pk=selected_activity_id)
        else:
            return StreetActivity.objects.first()

    def post(self, request, *args, **kwargs):
        """Save selected activity to session and redirect to assign activity"""
        activity_id = request.POST.get("activity_id")
        if activity_id:
            request.session["selected_activity_id"] = activity_id
        return redirect("assign-activity-to-moment")


class AssignActivityToMomentView(LoginRequiredMixin, View):
    """View to assign street activity to the moment being created"""

    def get(self, request, *args, **kwargs):
        """Assign activity to moment using session data and create moment"""
        moment_data = request.session.get("moment_data")
        selected_activity_id = request.session.get("selected_activity_id")
        experience_id = request.session.get("experience_id")
        redirect_response = self.redirect_to_moment_form_if_missing_data(
            moment_data, selected_activity_id, experience_id
        )
        if redirect_response:
            return redirect_response

        experience, experience_id = self.get_or_create_experience(
            experience_id, request.user
        )

        activity = get_object_or_404(StreetActivity, pk=selected_activity_id)

        self.create_moment(moment_data, experience, activity)

        process_xp_and_level(
            self.request, confidence_level=moment_data.get("confidence_level", 0)
        )

        clear_session_data(request)

        return redirect("experience-detail", pk=experience_id)

    def redirect_to_moment_form_if_missing_data(
        self, moment_data, selected_activity_id, experience_id
    ):
        """If required session data is missing, redirect to the appropiate moment form"""
        required_fields = ["report"]
        missing_fields = [field for field in required_fields \
                          if not moment_data or not moment_data.get(field)]
        if (
            missing_fields
            or not selected_activity_id
        ):
            if experience_id:
                url = reverse(
                    "add-moment-to-experience", kwargs={"experience_id": experience_id}
                )
            else:
                url = reverse("add-first-moment-to-experience")
            messages.warning(
                self.request, "Niet alles ingevuld. Vul alstublieft de verplichte velden in"
            )
            message = ''
            if missing_fields:
                message += f": {', '.join(missing_fields)}"
            if not selected_activity_id:
                message += ". Selecteer een activiteit."

            messages.warning(self.request, message)
            return redirect(url)
        return None

    def get_or_create_experience(self, experience_id, user):
        """Returns a tuple of experience instance and experience_id as string,
        by retrieving existing experience by ID or creating a new one"""
        if experience_id:
            try:
                experience = Experience.objects.get(pk=experience_id)
                return experience, str(experience_id)
            except Experience.DoesNotExist:
                pass
        experience = Experience.objects.create(user=user)
        return experience, str(experience.id)

    def create_moment(self, moment_data, experience, activity):
        """Given all the data for moment,
        save and return a created moment"""

        with transaction.atomic():
            moment = Moment(
                experience=experience,
                activity=activity,
                report=moment_data.get("report", ""),
                confidence_level=moment_data.get("confidence_level", 0),
                from_practitioner=moment_data.get("from_practitioner", True),
            )
            moment.save()
        return moment


class MomentUpdateView(UpdateView):
    """View to update an moment"""

    model = Moment
    form_class = MomentForm

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.object.activity
        context["ConfidenceLevel"] = ConfidenceLevel
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


class StartExperienceView(LoginRequiredMixin, TemplateView):
    """Navigates to the start experience page with a random sparkline of an experience"""

    template_name = "streetactivity/start_experience.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        random_experience = Experience.objects.order_by("?").first()
        if random_experience:
            example_moments_data = create_moment_data_of_experience_for_chart(random_experience)
            context['moments'] = example_moments_data[0]
            context["moments_json"] = example_moments_data[1]
        return context


class ExperienceDetailView(DetailView):
    """Detailview of experience with its related moments"""

    model = Experience
    context_object_name = "experience"

    def get_context_data(self, **kwargs):
        """Extend context data with moments and their data for chart"""
        context = super().get_context_data(**kwargs)
        context["user"] = self.object.user
        moment_data = create_moment_data_of_experience_for_chart(self.object)
        context["moments"] = moment_data[0]
        context["moments_json"] = moment_data[1]
        return context

def create_moment_data_of_experience_for_chart(experience):
    """Given an experience,
    create the moment data in json format for the chart of that experience"""
    moments = list(
            experience.moments.order_by("date_created").select_related("activity")
        )
    moment_data = []
    for moment in moments:
        moment_data.append(
            {
                "id": moment.id,
                "activity": {
                    "name": moment.activity.name,
                    "id": moment.activity.id,
                },
                "confidence_level": moment.confidence_level,
                "report": moment.report,
                "report_snippet": moment.report[:25] + "..."
                if moment.report and len(moment.report) > 25
                else moment.report,
                "from_practitioner": moment.from_practitioner,
            }
        )
    return moments, json.dumps(moment_data)

class ExperienceDeleteView(DeleteView):
    """View to delete an experience"""

    model = Experience
    template_name = CONFIRM_DELETE_TEMPLATE
    success_url = reverse_lazy("user")

    def get_success_url(self):
        return reverse_lazy("user", kwargs={"username": self.object.user.username})


class ExperienceViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Experience"""

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
