import pytest
from pytest_factoryboy import register
from django.test import Client
from faker import Faker
from travelingguestbook import factories
from travelingguestbook.factories import StreetActivityFactory

fake = Faker()

register(factories.StreetActivityFactory)

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    '''This function saves us from typing @pytest.mark.django_db before every test function'''
