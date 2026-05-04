import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.models import User
from core.utils.mixins import WordTreeMixin
from streetactivity.models import Word, StreetActivity
from .models import CookieConsentLog

class MailtoMixin:
    """Mixin that provides mailto_url context for templates"""

    def get_mailto_url(self):
        """Creates a mailto url for the admin"""
        admin = User.objects.filter(is_superuser=True).first()
        if admin and admin.email:
            return f"mailto:{admin.email}"
        else:
            return "mailto:admin@example.com"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        """Adds mailto_url to the context"""
        context = super().get_context_data(**kwargs)  # type: ignore[reportAttributeAccessIssue]
        context['mailto_url'] = self.get_mailto_url()
        return context

class HomeView(TemplateView, WordTreeMixin):
    """Renders the home page"""
    template_name = 'core/home.html'

    def get_wordtree_base_filter(self):
        """Base filter for home page: all words from past week."""
        return {
            'type': 'week',
            'value': timezone.now().strftime("%Y-%m-%d"),
            'display_name': 'Community words (past week)'
        }

    def get_base_queryset(self):
        """Get words from the past week."""
        one_week_ago = timezone.now() - timedelta(days=7)
        return Word.objects.filter(date_created__gte=one_week_ago)

    def get_context_data(self, **kwargs):
        """Add recent words and random activities to the home page"""
        context = super().get_context_data(**kwargs)
        
        # Featured activities
        featured_activities = StreetActivity.objects.order_by('?')
        context['featured_activities'] = featured_activities[:4]
        context['activities_remaining'] = max(0, featured_activities.count() - 4)
        
        # Recent words for display
        context['recent_words'] = Word.objects.order_by('-date_created')[:5]
        
        # Get unique words count
        context['unique_words'] = Word.objects.values('word').distinct().count()
        
        # Get top word
        top_word = Word.objects.values('word')\
            .annotate(count=Count('word'))\
            .order_by('-count')\
            .first()
        context['top_word'] = top_word['word'] if top_word else None
        
        # Add word tree data
        current_filters = {'date': 'week'}
        wordtree_context = self.get_wordtree_context(
            self.get_base_queryset(),
            current_filters
        )
        context.update(wordtree_context)
        context['wordtree_container_id'] = 'global'
        
        return context

class HelpView(TemplateView):
    """Renders the help page"""
    template_name = 'core/help.html'

class ContactView(MailtoMixin, TemplateView):
    """Renders the contact page with dynamic mailto_url"""
    template_name = 'core/contact.html'

class AboutView(TemplateView):
    """Renders the about page with dynamic mailto_url"""
    template_name = 'core/about.html'

@require_POST
def save_cookie_consent(request):
    """Saves the user's cookie consent and logs it in the database"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False}, status=400)
    CookieConsentLog.objects.create(
        user = request.user if request.user.is_authenticated else None,
        consent = data,
        ip = request.META.get('REMOTE_ADDR'),
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:1000]
    )
    resp = JsonResponse({'ok': True})
    resp.set_cookie('site_cookie_consent_v1',
                    json.dumps(data),
                    max_age=365*24*3600,
                    path='/',
                    samesite='Lax',
                    secure=True)
    return resp

class WordTreeTestView(TemplateView, WordTreeMixin):
    """A test page for the WordTree component"""
    template_name = 'core/wordtree_card.html'

    def get_wordtree_base_filter(self):
        """Base filter for the word tree test page: all words."""
        return {
            'type': 'all',
            'value': '',
            'display_name': 'All Words'
        }

    def get_base_queryset(self):
        """Get all words."""
        return Word.objects.all()