import pytest
from django.urls import reverse
from django.test import Client
from travelingguestbook.factories import RegistrationFactory

class TestRegistrationViews:
    '''Test suite for the registration views in the oogcontact app.'''
    @pytest.fixture
    def client(self):
        '''Fixture to create a test client for making requests to the views.'''
        return Client()

    def test_registration_detail_view(self, client):
        '''Test the registration detail view to ensure it returns a 200 status code and contains the expected context.'''
        registration = RegistrationFactory()
        response = client.get(reverse('registration_detail', args=[registration.number]))
        assert response.status_code == 200
        assert 'registration' in response.context

    def test_registration_create_view(self, client):
        '''Test the registration create view to ensure it returns a 200 status code and contains the expected form in context.'''
        response = client.get(reverse('registration_create'))
        assert response.status_code == 200
        assert 'form' in response.context
