import pytest
import uuid
from pytest_factoryboy import register
from travelingguestbook import factories

register(factories.GoalFactory)
register(factories.UserFactory)
register(factories.SociableFactory)
register(factories.LogMessageFactory)

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    '''This function saves us from typing @pytest.mark.django_db before every test function'''
    pass

@pytest.fixture
def test_password():
   return 'strong-test-pass'

  
@pytest.fixture
def create_user(db, django_user_model, test_password):
   def make_user(**kwargs):
       kwargs['password'] = test_password
       if 'username' not in kwargs:
           kwargs['username'] = str(uuid.uuid4())
       return django_user_model.objects.create_user(**kwargs)
   return make_user

@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
   def make_auto_login(user=None):
       if user is None:
           user = create_user()
       client.login(username=user.username, password=test_password)
       return client, user
   return make_auto_login