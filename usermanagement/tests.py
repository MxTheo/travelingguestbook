'''Followed the tutorial: https://djangostars.com/blog/django-pytest-testing/'''

from django.urls import reverse
from django.contrib.auth.models import User

def test_user_create(create_user):
    '''Given a user name John,
    tests if create_user creates user John'''
    create_user(username='John')
    assert User.objects.count() == 1

def test_view(client):
    '''Given the homepage,
    tests it the homepage is reached'''
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200

def test_auth_view(auto_login_user):
    '''Logged in,
    tests if the user reaches dashboard'''
    client, _ = auto_login_user()
    url = reverse('dashboard')
    response = client.get(url)
    assert response.status_code == 200
