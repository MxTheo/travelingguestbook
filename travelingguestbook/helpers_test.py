from django.urls import reverse
from faker import Faker
from sociablecreating.models import LogMessage, Sociable
from travelingguestbook.factories import ProfileFactory, SociableFactory
from usermanagement.models import Profile


def helper_test_page_rendering(client, name_of_page, keyword_arguments=None):
    '''Given, the client, a name of the page and optional keyword_arguments,
    tests if the client responds with OK, success'''
    url = reverse(name_of_page, kwargs=keyword_arguments)
    response = client.get(url)
    assert response.status_code == 200


def create_sociable(client, data=None):
    '''Given the client and optional data for the sociable,
    creates sociable using the CreateView for unittesting purposes'''
    if not data or 'description' not in data.keys():
        data = {
            'description': 'create_sociable'
        }
    client.post(reverse('create-sociable'), data=data)
    return Sociable.objects.get(description=data['description'])


def create_logmessage(client, sociable=None, data=None):
    '''Given the client and optional data for the sociable,
    creates a logmessage using the CreateView for unittesting purposes'''
    if sociable is None:
        sociable = SociableFactory()
    if data is None:
        data = {'name': 'create_logmessage', 'body': 'create_logmessage'}
    url_create = reverse('create-logmessage', args=[sociable.slug])
    client.post(url_create, data=data)
    return LogMessage.objects.filter(sociable=sociable)[0]


def create_user_and_profile_with_custom_description(auto_login_user, custom_descr='test123'):
    '''Given a custom description,
    creates a user with a profile with that custom description
    and returns the client and user'''
    client, user = auto_login_user()
    Profile.objects.get(user=user).delete()
    ProfileFactory(user=user, custom_description_for_code=custom_descr)
    return client, user
