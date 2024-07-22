from django.urls import reverse
from contact.views import create_mailto_url
from travelingguestbook.factories import UserFactory

def test_about(client):
    '''Test if about page is rendered'''
    UserFactory(username='admin')
    url = reverse('about')
    response = client.get(url)
    assert response.status_code == 200

def test_help(client):
    '''Test if help page is opened'''
    url = reverse('help')
    response = client.get(url)
    assert response.status_code == 200

class TestMailToUrl:
    '''Tests for the function create_mailto_url'''

    def setup_method(self):
        '''For every test, an admin account has to be created'''
        UserFactory(username='admin', email='test@info.com')

    def test_contact(self, client):
        '''Test if contact page is rendered with a dynamic mailto url'''
        url = reverse('contact')
        response = client.get(url)
        assert response.status_code == 200

    def test_create_mailto_url(self):
        '''Test if mailto redirects user to the mailto url with admin mail address'''
        mailto_url = create_mailto_url()
        assert mailto_url == 'mailto:test@info.com'
