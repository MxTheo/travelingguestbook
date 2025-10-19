import pytest
from pytest_factoryboy import register
from django.test import Client
from travelingguestbook import factories
from travelingguestbook.factories import StreetActivityFactory, SWOTElementFactory
from faker import Faker

fake = Faker()

register(factories.UserFactory)
register(factories.ChatRoomFactory)
register(factories.ChatMessageFactory)
register(factories.ExternalReferenceFactory)
register(factories.StreetActivityFactory)
register(factories.SWOTElementFactory)

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    '''This function saves us from typing @pytest.mark.django_db before every test function'''

@pytest.fixture
def swot_element():
    """Fixture providing a SWOT element"""
    return SWOTElementFactory()

@pytest.fixture
def street_activity():
    """Fixture providing a street activity"""
    return StreetActivityFactory()

@pytest.fixture
def client_with_session():
    """Fixture providing client with session support"""

    client = Client()
    # Ensure session is available
    client.get('/')  # This creates a session
    return client
