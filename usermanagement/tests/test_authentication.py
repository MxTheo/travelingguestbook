
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from travelingguestbook.factories import UserFactory
from usermanagement.views import dashboard


class TestDashboard:
    def test_dashboard_authenticated(self, auto_login_user):
        url = reverse('dashboard')
        request = RequestFactory().get(url)
        request.user = UserFactory()
        response = dashboard(request)
        assert response.status_code == 200

    def test_dashboard_unauthenticated(self):
        url = reverse('dashboard')
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        response = dashboard(request)
        assert response.status_code == 302