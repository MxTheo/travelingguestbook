from django.urls import reverse

from travelingguestbook.factories import UserFactory

def helper_test_page_rendering(client, name_of_page, arguments=None):
    url = reverse(name_of_page, args=arguments)
    response = client.get(url)
    assert response.status_code == 200

def login_user(client):
    '''Custom login fixtur according to https://djangostars.com/blog/django-pytest-testing/,
    to log in for test'''
    user = UserFactory()
    client.login(username=user.username, password=user.password)
    return client, user