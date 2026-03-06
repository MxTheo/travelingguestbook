# streetgame/mixins.py
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from streetactivity.models import Word, StreetActivity


class WordTreeMixin:
    """
    Mixin to provide word tree functionality for views.
    Handles filtering and word frequency calculation.

    Usage:
        class MyView(WordTreeMixin, DetailView):
            def get_base_queryset(self):
                return Word.objects.filter(...)

            def get_wordtree_base_filter(self):
                return {'type': 'mytype', 'value': self.object.id}
    """

    def get_wordtree_base_filter(self):
        """
        Get the base filter for this view.

        Returns:
            dict: With keys 'type', 'value', and optional 'display_name'
        """
        return {
            'type': 'all',
            'value': '',
            'display_name': 'All words'
        }

    def get_base_queryset(self):
        """
        Get the base queryset for words.
        Should be overridden by child classes.

        Returns:
            QuerySet: Base Word queryset for this view
        """
        return Word.objects.all()

    def apply_date_filter(self, queryset, date_filter):
        """
        Apply date filter to queryset.

        Args:
            queryset: Base Word queryset
            date_filter: 'all', 'today', 'week', or 'month'

        Returns:
            QuerySet: Filtered by date
        """
        if date_filter == 'all':
            return queryset

        now = timezone.now()

        if date_filter == 'today':
            return queryset.filter(date_created__date=now.date())
        elif date_filter == 'week':
            return queryset.filter(date_created__gte=now - timedelta(days=7))
        elif date_filter == 'month':
            return queryset.filter(date_created__gte=now - timedelta(days=30))

        return queryset

    def apply_activity_filter(self, queryset, activity_filter):
        """
        Apply activity filter to queryset.

        Args:
            queryset: Base Word queryset
            activity_filter: 'all' or activity ID

        Returns:
            QuerySet: Filtered by activity
        """
        if activity_filter and activity_filter != 'all':
            try:
                activity_id = int(activity_filter)
                StreetActivity.objects.get(id=activity_id)
                return queryset.filter(activity_id=activity_id)
            except (ValueError, TypeError, StreetActivity.DoesNotExist):
                pass
        return queryset

    def get_word_frequencies(self, queryset, limit=50):
        """
        Calculate word frequencies from queryset.

        Args:
            queryset: Filtered Word queryset
            limit: Maximum number of words to return

        Returns:
            list: [{'word': 'courage', 'weight': 5}, ...]
        """
        frequencies = queryset.values('word').annotate(
            weight=Count('word')
        ).order_by('-weight')[:limit]

        return [
            {
                'word': item['word'],
                'weight': item['weight'],
            }
            for item in frequencies
        ]

    def get_date_filter_options(self):
        """Get available date filter options for UI."""
        return [
            {'value': 'all', 'label': 'All time'},
            {'value': 'today', 'label': 'Today'},
            {'value': 'week', 'label': 'Past week'},
            {'value': 'month', 'label': 'Past month'},
        ]

    def get_wordtree_context(self, base_queryset, current_filters):
        """
        Build the word tree context data.

        Args:
            base_queryset: The base queryset to filter
            current_filters: Dict with current filter values
                {
                    'date': 'all'|'today'|'week'|'month',
                    'activity': 'all'|<activity_id>
                }

        Returns:
            dict: Context data for the word tree template
        """
        # Apply filters sequentially
        filtered_queryset = base_queryset
        filtered_queryset = self.apply_date_filter(
            filtered_queryset, 
            current_filters.get('date', 'all')
        )
        filtered_queryset = self.apply_activity_filter(
            filtered_queryset,
            current_filters.get('activity', 'all')
        )

        # Calculate word frequencies
        word_frequencies = self.get_word_frequencies(filtered_queryset)

        return {
            'wordtree_data': {
                'words': word_frequencies,
                'total_count': filtered_queryset.count(),
                'base_filter': self.get_wordtree_base_filter(),
                'current_filters': current_filters,
            },
            'date_filter_options': self.get_date_filter_options(),
            'current_date_filter': current_filters.get('date', 'all'),
        }


class ActivityFilterMixin(WordTreeMixin):
    """
    Mixin for views that need activity filtering capability.
    Adds activity filter options to context.

    Usage:
        class MyView(ActivityFilterMixin, DetailView):
            def get_base_queryset(self):
                return Word.objects.filter(...)
    """

    def get_activity_filter_options(self, base_queryset):
        """
        Get available activity filter options based on queryset.

        Args:
            base_queryset: The base queryset to extract activities from

        Returns:
            list: [{'value': 'all', 'label': 'All activities'}, ...]
        """
        # Get distinct activities from the queryset
        activities = StreetActivity.objects.filter(
            words__in=base_queryset
        ).distinct().order_by('name')

        options = [{'value': 'all', 'label': 'All activities'}]
        for activity in activities:
            options.append({
                'value': activity.id,
                'label': activity.name
            })
        return options

    def get_wordtree_context(self, base_queryset, current_filters):
        """
        Extend base wordtree context with activity filter options.

        Args:
            base_queryset: The base queryset to filter
            current_filters: Dict with current filter values

        Returns:
            dict: Extended context with activity filter options
        """
        context = super().get_wordtree_context(base_queryset, current_filters)

        context['activity_filter_options'] = self.get_activity_filter_options(base_queryset)
        context['current_activity_filter'] = current_filters.get('activity', 'all')

        return context