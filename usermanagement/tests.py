'''Followed the tutorial: https://djangostars.com/blog/django-pytest-testing/'''

from django.urls import reverse
from django.contrib.auth.models import User
from travelingguestbook.helpers_test import helper_test_page_rendering

def test_user_create(create_user):
    '''Given a user name John,
    tests if create_user creates user John'''
    create_user(username='John')
    assert User.objects.count() == 1

def test_view(client):
    '''Given the homepage,
    tests it the homepage is reached'''
    helper_test_page_rendering(client, 'home')

def test_auth_view(auto_login_user):
    '''Logged in,
    tests if the user reaches dashboard'''
    client, _ = auto_login_user()
    helper_test_page_rendering(client, 'dashboard')
