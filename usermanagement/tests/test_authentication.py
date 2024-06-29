from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from travelingguestbook.factories import UserFactory
from usermanagement.views import dashboard


class TestDashboard:
    '''Test the redirecting behaviour for user permissions for the dashboard'''
    def test_dashboard_authenticated(self):
        '''Logged in as a user,
        tests if the user is redirected towards its dashboard'''
        url = reverse('dashboard')
        request = RequestFactory().get(url)
        request.user = UserFactory()
        response = dashboard(request)
        assert response.status_code == 200

    def test_dashboard_unauthenticated(self):
        '''Not logged in as a user,
        tests if the anonymous user is redirected to a not allowed page'''
        url = reverse('dashboard')
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        response = dashboard(request)
        assert response.status_code == 302
