import uuid
import pytest
from pytest_factoryboy import register
from travelingguestbook import factories

register(factories.GoalFactory)
register(factories.UserFactory)
register(factories.SociableFactory)
register(factories.LogMessageFactory)

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    '''This function saves us from typing @pytest.mark.django_db before every test function'''

@pytest.fixture(name='create_user')
def create_user(django_user_model):
    '''Custom user fixture according to https://djangostars.com/blog/django-pytest-testing/,
    to create a test user'''
    def make_user(**kwargs):
        kwargs['password'] = 'strong-test-pass'
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)
    return make_user

@pytest.fixture
def auto_login_user(client, create_user):
    '''Custom login fixtur according to https://djangostars.com/blog/django-pytest-testing/,
    to log in for test'''
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.username, password='strong-test-pass')
        return client, user
    return make_auto_login
