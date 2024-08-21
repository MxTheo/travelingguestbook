from django.urls import reverse
from faker import Faker
from sociablecreating.models import Sociable


def helper_test_page_rendering(client, name_of_page, keyword_arguments=None):
    '''Given, the client, a name of the page and optional keyword_arguments,
    tests if the client responds with OK, success'''
    url = reverse(name_of_page, kwargs=keyword_arguments)
    response = client.get(url)
    assert response.status_code == 200


fake = Faker()


def create_sociable(client, data=None):
    '''Given the client and optional data for the sociable,
    creates sociables using the CreateView for unittesting purposes'''
    if data is None:
        data = {
            'description': fake.text()
        }
    client.post('/create-sociable/', data=data)
    return Sociable.objects.get(description=data['description'])
