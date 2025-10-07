from django.urls import reverse
from travelingguestbook.factories import UserFactory
from travelingguestbook.helpers_test import helper_test_page_rendering 
from core.views import MailtoMixin, ContactView, TemplateView

def test_about(client):
    """Test if about page is rendered"""
    UserFactory(is_superuser=True)
    helper_test_page_rendering(client, "about")

def test_help(client):
    """Test if help page is opened"""
    helper_test_page_rendering(client, "help")

def test_contact(client):
    """Test if contact page is rendered with a dynamic mailto url"""
    UserFactory(is_superuser=True)
    helper_test_page_rendering(client, "contact")

class TestMailToUrl:
    """Tests for the mailto url functionality"""

    def test_contact_view_mailto_url(self):
        """Test that ContactView creates correct mailto url"""
        UserFactory(email="test@info.com", is_superuser=True)
        view = ContactView()
        mailto_url = view.get_mailto_url()
        assert mailto_url == "mailto:test@info.com"

    def test_contact_page_contains_mailto_link(self, client):
        """Test that contact page contains the mailto link"""
        UserFactory(email="page@test.com", is_superuser=True)
        response = client.get(reverse('contact'))
        assert 'mailto:page@test.com' in response.content.decode()

    def test_mailto_url_without_admin(self):
        """Test mailto url fallback when no admin exists"""
        view = ContactView()
        mailto_url = view.get_mailto_url()
        assert mailto_url == "mailto:admin@example.com"

    def test_mailto_url_with_admin_no_email(self):
        """Test mailto url fallback when admin has no email"""
        UserFactory(email="", is_superuser=True)
        view = ContactView()
        mailto_url = view.get_mailto_url()
        assert mailto_url == "mailto:admin@example.com"

    def test_mailto_url_multiple_admins_uses_first(self):
        """Test that mailto url uses first admin when multiple exist"""
        UserFactory(email="", is_superuser=True, username="admin1")
        UserFactory(email="second@test.com", is_superuser=True, username="admin2")
        view = ContactView()
        mailto_url = view.get_mailto_url()
        assert mailto_url == "mailto:admin@example.com"

class TestMailtoMixin:
    """Tests for the MailtoMixin if you're using that approach"""

    def test_mixin_get_mailto_url(self):
        """Test MailtoMixin get_mailto_url method"""
        UserFactory(email="mixin@test.com", is_superuser=True)
        mixin = MailtoMixin()
        mailto_url = mixin.get_mailto_url()
        assert mailto_url == "mailto:mixin@test.com"

    def test_mixin_get_context_data(self):
        """Test that MailtoMixin adds mailto_url to context"""
        UserFactory(email="context@test.com", is_superuser=True)

        class TestView(MailtoMixin, TemplateView):
            """Test view using MailtoMixin"""
            template_name = 'core/test.html'

        view = TestView()
        context = view.get_context_data()

        assert 'mailto_url' in context
        assert context['mailto_url'] == "mailto:context@test.com"
