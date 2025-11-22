from django.urls import reverse
from django.contrib import auth
from travelingguestbook.helpers_test import helper_test_page_rendering
from travelingguestbook.factories import UserFactory
from usermanagement.forms import RegisterForm
from usermanagement.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile

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

class TestProfile():
    """Tests for the profile of a user"""
    def test_if_profile_is_created(self):
        '''Test if a profile is created when a new user is created'''
        user    = UserFactory()
        profile = Profile.objects.get(user=user)
        assert str(profile) == f"Profile of '{user.username}'"

    def test_if_profile_is_edited(self):
        """Test if a profile lvl is changed, when the user is saved"""
        user = UserFactory()
        user.profile.lvl = 1
        user.save()
        profile = Profile.objects.get(user=user)
        assert profile.lvl == 1

class TestUserUpdateView():
    """Tests for user that updates its account"""
    def test_login_required_redirects(self, client):
        """Anonymous users should be redirected to login when accessing the update page."""
        url = reverse('update-account')
        resp = client.get(url)
        assert resp.status_code in (302, 301)
        assert '/login' in resp['Location']

    def test_get_shows_both_forms(self, auto_login_user):
        """Logged in user sees both user and profile form fields."""
        client, user = auto_login_user()
        resp = client.get(reverse('update-account'))
        content = resp.content.decode()
        assert 'email' in content
        assert 'lvl' in content

    def test_post_valid_updates_user_and_profile(self, auto_login_user):
        """Submitting valid data updates User and Profile and redirects."""
        client, user = auto_login_user()
        url = reverse('update-account')

        new_email = 'updated@example.com'
        new_lvl = 2

        data = {
            'username': user.username,
            'email': new_email,
            'lvl': new_lvl,
        }

        resp = client.post(url, data)
        # successful save should redirect
        assert resp.status_code in (302, 301)

        user.refresh_from_db()
        profile = Profile.objects.get(user=user)
        assert user.email == new_email
        assert profile.lvl == new_lvl

    def test_post_invalid_shows_errors(self, auto_login_user):
        """Submitting invalid data redisplays the form with errors."""
        client, user = auto_login_user()
        url = reverse('update-account')

        data = {
            'username': user.username,
            'email': 'invalid-email',  # not a valid email -> form should be invalid
            'lvl': user.profile.lvl,
        }

        resp = client.post(url, data)
        assert resp.status_code == 200
        assert 'edit je account' in resp.content.decode().lower()

class TestProfileImage():
    """Tests that the user can set a profile image"""
    def test_profile_image_url_without_profile_image(self):
        """Test profile_image_url property when no profile_image is set"""
        user = UserFactory()
        
        assert user.profile.profile_image_url == '/static/persona/images/empty_portrait.jpg'
    
    def test_profile_image_url_with_profile_image(self, auto_login_user):
        """Test profile_image_url property when profile_image is set"""
        mock_image = SimpleUploadedFile(
            "test.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        _, user = auto_login_user()
        user.profile.profile_image = mock_image
        user.save()
        profile = Profile.objects.get(user=user)

        assert not profile.profile_image_url == '/static/persona/images/empty_portrait.jpg'

    def test_update_profile_with_profile_image(self, auto_login_user):
        """Test that the default profile image is not shown when user updates its profile image"""
        client, _ = auto_login_user()
        mock_image = SimpleUploadedFile(
            "test.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        url = reverse('update-account')
        data = {
            'profile_image': mock_image,
        }
        response = client.post(url, data, follow=True)
        assert 'profileimage' in response.content.decode()
