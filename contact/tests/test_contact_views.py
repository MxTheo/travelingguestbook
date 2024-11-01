from contact.views import create_mailto_url
from travelingguestbook.factories import UserFactory
from travelingguestbook.helpers_test import helper_test_page_rendering


def test_about(client):
    """Test if about page is rendered"""
    UserFactory(is_superuser=True)
    helper_test_page_rendering(client, "about")


def test_help(client):
    """Test if help page is opened"""
    helper_test_page_rendering(client, "help")


class TestMailToUrl:
    """Tests for the function create_mailto_url"""

    def setup_method(self):
        """For every test, an admin account has to be created"""
        UserFactory(email="test@info.com", is_superuser=True)

    def test_contact(self, client):
        """Test if contact page is rendered with a dynamic mailto url"""
        helper_test_page_rendering(client, "contact")

    def test_create_mailto_url(self):
        """Test if mailto redirects user to the mailto url with admin mail address"""
        mailto_url = create_mailto_url()
        assert mailto_url == "mailto:test@info.com"
