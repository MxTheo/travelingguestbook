from django.urls import reverse
from django.contrib import auth
from usermanagement.forms import RegisterForm
from travelingguestbook.helpers_test import helper_test_page_rendering

class TestRegister():
    '''Tests for registering a new user'''
    register_url = reverse('register')

    def setup_method(self):
        '''Every test needs to have this data, independant of other tests ran previously'''
        self.data_correct = {
            'username': 'test',
            'email': 'test@test.nl',
            'password1': 'Pass123!',
            'password2': 'Pass123!'}

    def test_page_renderd(self, client):
        '''Test if register page is rendered'''
        helper_test_page_rendering(client, 'register')

    def test_form_correct_without_first_and_last_name(self):
        '''Test if is valid returns true, when registerform is entered with correct data,
        without first and last name'''
        form = RegisterForm(self.data_correct)
        assert form.is_valid()

    def test_form_has_unequal_passwords(self):
        '''Test if is valid returns falls, when the passwords are unequal'''
        data_incorrect              = self.data_correct
        data_incorrect['password1'] = 'Pass123?'
        form                        = RegisterForm(data_incorrect)
        assert not form.is_valid()

    def test_register_validform_view(self, client):
        '''Test if the client redirects towards the dashboard, after correctly filling in the form'''
        response = client.post(self.register_url, self.data_correct)
        assert response.status_code == 302

    def test_registered_user_logged_in(self, client):
        '''Test if the user is logged in, after correctly filling in the form'''
        client.post(self.register_url, self.data_correct)
        user = auth.get_user(client)
        assert user.is_authenticated
