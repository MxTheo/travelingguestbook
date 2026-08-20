import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from streetactivity.models import Reflection, StreetActivity, StreetActivityPhoto

from .models import CookieConsentLog


class HomeView(TemplateView):
    """Renders the home page"""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        """Add recent reflections and random activities to the home page"""
        context = super().get_context_data(**kwargs)
        featured_activities = StreetActivity.objects.order_by('?')
        context['recent_reflections'] = Reflection.objects.select_related('activity').all()[:3]
        context['featured_activities'] = featured_activities[:4]
        context['activities_remaining'] = max(0, featured_activities.count() - 4)
        context['photos'] = StreetActivityPhoto.objects.order_by('?')[:4]
        return context

class HelpView(TemplateView):
    """Renders the help page"""
    template_name = 'core/help.html'

class ContactView(TemplateView):
    """Renders the contact page"""
    template_name = 'core/contact.html'

class AboutView(TemplateView):
    """Renders the about page"""
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
