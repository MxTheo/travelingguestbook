from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse
from django.contrib import auth
from travelingguestbook.factories import UserFactory
from usermanagement.views import dashboard
from travelingguestbook.helpers_test import helper_test_page_rendering
from usermanagement.forms import RegisterForm

class TestRegister():
    register_url = reverse('register')

    def setup_method(self):
        self.data_correct = {'username': 'test', 'email':'test@test.nl', 'password1': 'Pass123!', 'password2': 'Pass123!'}

    def test_page_renderd(self, client):
        '''Test if register page is rendered'''
        helper_test_page_rendering(client, 'register')

    def test_form_correct_without_first_and_last_name(self):
        '''Test if is valid returns true, when registerform is entered with correct data, without first and last name'''
        form = RegisterForm(self.data_correct)

        assert form.is_valid()

    def test_form_has_unequal_passwords(self):
        '''Test if is valid returns falls, when the passwords are unequal'''
        data_incorrect = self.data_correct
        data_incorrect['password1'] = 'Pass123?'
        form = RegisterForm(data_incorrect)

        assert form.is_valid() == False

    def test_register_validform_view(self, client):
        '''Test if the client redirects towards the dashboard, after correctly filling in the form'''
        response = client.post(self.register_url, self.data_correct)

        assert 'dashboard' in response.url

    def test_registered_user_logged_in(self, client):
        '''Test if the user is logged in, after correctly filling in the form'''
        client.post(self.register_url, self.data_correct)
        user = auth.get_user(client)
        assert user.is_authenticated

    def test_user_invalid_not_logged_in(self, client):
        '''Test if user enters incorrect, it remains at the register page'''
        data_incorrect = self.data_correct
        data_incorrect['password1'] = 'incorrect'
        response = client.post(self.register_url, data_incorrect)

        assert 'register' in response.rendered_content

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
