from django.urls import reverse
from sociablecreating.models import LogMessage
from travelingguestbook.factories import SociableFactory


def helper_test_page_rendering(client, name_of_page, keyword_arguments=None):
    '''Given, the client, a name of the page and optional keyword_arguments,
    tests if the client responds with OK, success'''
    url = reverse(name_of_page, kwargs=keyword_arguments)
    response = client.get(url)
    assert response.status_code == 200


def create_logmessage(client, sociable=None, data=None):
    '''Given the client and optional data for the sociable,
    creates a logmessage using the CreateView for unittesting purposes'''
    if sociable is None:
        sociable = SociableFactory()
    if data is None:
        data = {'name': 'create_logmessage', 'body': 'create_logmessage', 'to_person':'create_logmessage'}
    url_create = reverse('create-logmessage', args=[sociable.slug])
    client.post(url_create, data=data)
    return LogMessage.objects.filter(sociable=sociable)[0]
