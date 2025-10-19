from django.views.generic import TemplateView
from django.contrib.auth.models import User

class MailtoMixin:
    """Mixin that provides mailto_url context for templates"""

    def get_mailto_url(self):
        """Creates a mailto url for the admin"""
        admin = User.objects.filter(is_superuser=True).first()
        if admin and admin.email:
            return f"mailto:{admin.email}"
        else:
            return "mailto:admin@example.com"

    
    def get_context_data(self, **kwargs):
        """Adds mailto_url to the context"""
        context = super().get_context_data(**kwargs)
        context['mailto_url'] = self.get_mailto_url()
        return context

class HomeView(TemplateView):
    """Renders the home page"""
    template_name = 'core/home.html'

class HelpView(TemplateView):
    """Renders the help page"""
    template_name = 'core/help.html'

class ContactView(MailtoMixin, TemplateView):
    """Renders the contact page with dynamic mailto_url"""
    template_name = 'core/contact.html'

class AboutView(TemplateView):
    """Renders the about page with dynamic mailto_url"""
    template_name = 'core/about.html'
