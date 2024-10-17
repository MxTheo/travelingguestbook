'''Followed the tutorial: https://djangostars.com/blog/django-pytest-testing/'''
from travelingguestbook.helpers_test import helper_test_page_rendering


def test_view(client):
    '''Given the homepage,
    tests it the homepage is reached'''
    helper_test_page_rendering(client, 'home')


def test_auth_view(auto_login_user):
    '''Logged in,
    tests if the user reaches dashboard'''
    client, _ = auto_login_user()
    helper_test_page_rendering(client, 'dashboard_sociable')
