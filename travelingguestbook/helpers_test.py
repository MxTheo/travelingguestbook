from django.urls import reverse
from faker import Faker
from goalmanagement.models import Goal
from sociablecreating.models import Sociable


def helper_test_page_rendering(client, name_of_page, arguments=None):
    '''Given, the client, a name of the page and optional arguments,
    tests if the client responds with OK, success'''
    url = reverse(name_of_page, args=arguments)
    response = client.get(url)
    assert response.status_code == 200


fake = Faker()


def create_goal(client, data=None):
    '''Given the client and optional data for the goal,
    creates goals using the CreateView for unittesting purposes'''
    url_create = reverse('create-goal')
    if data is None:
        data         = {'title': fake.text(max_nb_chars=145)}
    client.post(url_create, data)
    return Goal.objects.get(title=data['title'])


def create_sociable(client, data=None):
    '''Given the client and optional data for the sociable,
    creates sociables using the CreateView for unittesting purposes'''
    create_goal(client)
    value_goal = Goal.objects.all().count()
    if data is None:
        data = {
            'goal'       : str(value_goal),
            'description': fake.text()
        }
    client.post('/create-sociable/', data=data)
    return Sociable.objects.get(description=data['description'])
