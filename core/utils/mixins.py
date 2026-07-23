# streetgame/mixins.py
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from streetactivity.models import Reflection, StreetActivity



class ActivityFilterMixin():
    """
    Mixin for views that need activity filtering capability.
    Adds activity filter options to context.

    Usage:
        class MyView(ActivityFilterMixin, DetailView):
            def get_base_queryset(self):
                return Reflection.objects.filter(...)
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
            reflections__in=base_queryset
        ).distinct().order_by('name')

        options = [{'value': 'all', 'label': 'All activities'}]
        for activity in activities:
            options.append({
                'value': activity.id,
                'label': activity.name
            })
        return options