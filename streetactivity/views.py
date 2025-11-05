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
from .models import StreetActivity, Experience, Tag
from .forms import (
    ExperienceForm,
    StreetActivityForm,
    TagForm,
)
from .models import NVC_CHOICES


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
        """Extend context data with experience statistics and tag data for charts and wordclouds."""
        context = super().get_context_data(**kwargs)
        activity = self.object

        experiences = activity.experiences.all()

        context["experiences_count"] = experiences.count()
        context["practitioner_count"] = experiences.filter(
            from_practitioner=True
        ).count()
        context["passerby_count"] = experiences.filter(from_practitioner=False).count()

        def get_chart_data(queryset):
            fase_counts = queryset.values("fase").annotate(count=Count("fase"))
            data = {"pioneer": 0, "intermediate": 0, "climax": 0}
            for item in fase_counts:
                data[item["fase"]] = item["count"]
            return data

        context["chart_data_everyone"] = get_chart_data(experiences)
        context["chart_data_practitioners"] = get_chart_data(
            experiences.filter(from_practitioner=True)
        )
        context["chart_data_passersby"] = get_chart_data(
            experiences.filter(from_practitioner=False)
        )

        def get_tag_data(queryset):
            """Retrieve top tags with counts for a given queryset
            of experiences for the wordcloud."""
            tags = (
                Tag.objects.filter(experiences__in=queryset)
                .annotate(count=Count("experiences"))
                .order_by("-count")[:20]
            )
            return list(tags.values("id", "name", "nvc_category", "count"))

        context["tag_data_everyone"] = get_tag_data(experiences)
        context["tag_data_practitioners"] = get_tag_data(
            experiences.filter(from_practitioner=True)
        )
        context["tag_data_passersby"] = get_tag_data(
            experiences.filter(from_practitioner=False)
        )

        context["all_tags"] = (
            Tag.objects.filter(experiences__activity=activity)
            .annotate(count=Count("experiences"))
            .order_by("-count")[:20]
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
    template_name = "admin/confirm_delete.html"
    success_url = reverse_lazy("streetactivity-list")


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
        """Extend context data with organized tags for selection."""
        context = super().get_context_data(**kwargs)
        activity_id = self.kwargs["pk"]
        context["activity"] = get_object_or_404(StreetActivity, pk=activity_id)

        # Get organized tags as a list for template
        organized_data = self.get_organized_tags()
        context["organized_tags_list"] = [
            {
                "nvc_category": nvc_value,
                "category_name": nvc_data["label"],
                "main_tags": nvc_data["main_tags"],
            }
            for nvc_value, nvc_data in organized_data.items()
        ]

        return context

    def get_organized_tags(self):
        """Organize tags by NVC category, then main tags and their subtags"""
        organized = {}

        for nvc_value, nvc_label in NVC_CHOICES:
            organized[nvc_value] = {"label": nvc_label, "main_tags": []}

        main_tags = Tag.objects.filter(maintag__isnull=True).prefetch_related("subtags")

        for main_tag in main_tags:
            nvc_category = main_tag.nvc_category

            main_tag_data = {"tag": main_tag, "subtags": list(main_tag.subtags.all())}

            organized[nvc_category]["main_tags"].append(main_tag_data)

        return organized

    def form_valid(self, form):
        activity_id = self.kwargs["pk"]
        form.instance.activity_id = activity_id
        if "beoefenaar" in self.request.path:
            form.instance.from_practitioner = True
        else:
            form.instance.from_practitioner = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "streetactivity-detail", kwargs={"pk": self.object.activity.pk}
        )


class TagListView(ListView):
    """View to list all tags."""

    model = Tag
    context_object_name = "tags"

    def get_context_data(self, **kwargs):
        """Extend context data to organize tags by category."""
        context = super().get_context_data(**kwargs)

        categories = {
            "needs": {
                "name": "Behoeften",
                "color": "success",
                "icon": "heart-fill",
                'description': 'Fundamentele menselijke behoeften die bijdragen aan welzijn',
                "maintags": Tag.objects.filter(
                    nvc_category="needs", maintag__isnull=True
                ).prefetch_related("subtags", "experiences"),
                "tags": Tag.objects.filter(nvc_category="needs"),
            },
            "feelings_fulfilled": {
                "name": "Gevoelens bij Vervulde Behoeften",
                "color": "info",
                "icon": "emoji-smile-fill",
                'description': 'Emoties die ontstaan wanneer behoeften worden vervuld',
                "maintags": Tag.objects.filter(
                    nvc_category="feelings_fulfilled", maintag__isnull=True
                ).prefetch_related("subtags", "experiences"),
                "tags": Tag.objects.filter(nvc_category="feelings_fulfilled"),
            },
            "feelings_unfulfilled": {
                "name": "Gevoelens bij Onvervulde Behoeften",
                "color": "info",
                "icon": "emoji-frown-fill",
                'description': 'Emoties die ontstaan wanneer behoeften niet worden vervuld',
                "maintags": Tag.objects.filter(
                    nvc_category="feelings_unfulfilled", maintag__isnull=True
                ).prefetch_related("subtags", "experiences"),
                "tags": Tag.objects.filter(nvc_category="feelings_unfulfilled"),
            },
            "other": {
                "name": "Overige tags",
                "color": "secondary",
                "icon": "tag-fill",
                'description': 'Tags die niet direct onder de andere categorieën vallen',
                "maintags": Tag.objects.filter(
                    nvc_category="other", maintag__isnull=True
                ).prefetch_related("subtags", "experiences"),
                "tags": Tag.objects.filter(nvc_category="other"),
            },
        }
        context["categories"] = categories
        return context


class TagDetailView(DetailView):
    """View to display details of a single tag."""

    model = Tag
    context_object_name = "tag"


class TagCreateView(CreateView):
    """View to create a new tag."""

    model = Tag
    form_class = TagForm

    def get_success_url(self):
        return reverse_lazy("tag-list")
