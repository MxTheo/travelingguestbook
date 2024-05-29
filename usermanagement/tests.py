from django.urls import reverse
import pytest
from django.contrib.auth.models import User
import uuid

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

def test_user_create(create_user):
  create_user(username='John')
  assert User.objects.count() == 1

def test_view(client):
   url = reverse('home')
   response = client.get(url)
   assert response.status_code == 200

def test_auth_view(auto_login_user):
   client, _ = auto_login_user()
   url = reverse('dashboard')
   response = client.get(url)
   assert response.status_code == 200
