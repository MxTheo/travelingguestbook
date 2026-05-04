from travelingguestbook.factories import UserFactory
from travelingguestbook.helpers_test import helper_test_page_rendering

def test_about(client):
    """Test if about page is rendered"""
    UserFactory(is_superuser=True)
    helper_test_page_rendering(client, "about")

def test_help(client):
    """Test if help page is opened"""
    helper_test_page_rendering(client, "help")

def test_contact(client):
    """Test if contact page is rendered """
    UserFactory(is_superuser=True)
    helper_test_page_rendering(client, "contact")
