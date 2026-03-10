from typing import Optional
from rest_framework import viewsets
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    TemplateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from core.utils.mixins import WordTreeMixin
from .serializers import StreetActivitySerializer, WordSerializer
from .models import StreetActivity, Word
from .forms import (
    WordForm,
    StreetActivityForm,
)

CONFIRM_DELETE_TEMPLATE = "admin/confirm_delete.html"

class WordTreeView(TemplateView):
    """View to display the word tree visualization."""

    template_name = "streetactivity/wordtree.html"

class StreetActivityListView(ListView):
    """View to list all street activities with filtering options."""

    model = StreetActivity
    context_object_name = "activities"
    paginate_by = 10


class StreetActivityDetailView(DetailView, WordTreeMixin):
    """View to display details of a single street activity."""
    model = StreetActivity
    context_object_name = "activity"

    def get_wordtree_base_filter(self):
        """Base filter: this specific activity."""
        activity = self.get_object()
        return {
            'type': 'activity',
            'value': activity.id,
            'display_name': activity.name
        }

    def get_base_queryset(self):
        """Base queryset: all words for this activity."""
        activity = self.get_object()
        return Word.objects.filter(activity=activity)

    def get_context_data(self, **kwargs):
        """Extend context data with word statistics for charts"""
        context = super().get_context_data(**kwargs)
        activity = self.object

        words = activity.words.all()
        words_count = words.count()

        context["words_count"] = words_count
        context["recent_words"] = words[:3]
        context["words_remaining"] = max(0, words_count - 3)

        context = self.add_word_tree_data(activity, context)
        return context

    def add_word_tree_data(self, activity, context):
        """Given an activity,
        get the current filters form request and the word tree context,
        update context and calculate activity specific statistics
        return context"""
        # Get current filters from request
        current_filters = {
            'date': self.request.GET.get('date_filter', 'all'),
            'activity': 'all',  # Activity is fixed, so no activity filter needed
        }

        # Get word tree context
        wordtree_context = self.get_wordtree_context(
            self.get_base_queryset(),
            current_filters
        )
        context.update(wordtree_context)
        context['wordtree_container_id'] = f"activity-{activity.id}"

        # Activity-specific stats
        all_words = self.get_base_queryset()
        context['total_words'] = all_words.count()
        context['unique_words'] = all_words.values('word').distinct().count()
        context['recent_words'] = all_words.order_by('-date_created')[:5]

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


class WordListView(ListView):
    """View to list all words."""

    model = Word
    context_object_name = "words"
    paginate_by = 10


class WordListViewStreetActivity(WordListView):
    """View to list words related to a specific street activity."""

    def get_queryset(self):
        """Filter words by street activity ID from URL."""
        activity_id = self.kwargs["pk"]
        return Word.objects.filter(activity_id=activity_id)

    def get_context_data(self, **kwargs):
        """Add street activity to context for header."""
        context = super().get_context_data(**kwargs)
        context["street_activity"] = get_object_or_404(
            StreetActivity, pk=self.kwargs["pk"]
        )
        return context


class WordDetailView(DetailView):
    """View to display details of a single word."""

    model = Word
    context_object_name = "word"


class WordCreateView(CreateView):
    """Create view for a single word"""

    model = Word
    form_class = WordForm
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
            "Bedankt voor het delen van jouw woord! "
            "Dit helpt anderen dit spel te begrijpen.",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "word-list-streetactivity",
            kwargs={"pk": self.object.activity.pk},  # type: ignore[reportOptionalMemberAccess]
        )

class WordUpdateView(UpdateView):
    """View to update an word"""

    model = Word
    form_class = WordForm

    def get_context_data(self, **kwargs):
        """Extend context data"""
        context = super().get_context_data(**kwargs)
        context["activity"] = self.object.activity
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.WARNING, "Het word is aangepast.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "word-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )


class WordDeleteView(DeleteView):
    """View to delete an word"""

    model = Word
    template_name = CONFIRM_DELETE_TEMPLATE

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.WARNING, "Het woord is verwijderd."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "word-list-streetactivity", kwargs={"pk": self.object.activity.pk}
        )

class WordViewSet(viewsets.ModelViewSet):
    """API endpoint that provides full CRUD for Word"""

    queryset = Word.objects.all()
    serializer_class = WordSerializer
