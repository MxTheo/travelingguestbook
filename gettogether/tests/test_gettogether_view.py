from django.urls import reverse
from django.utils import timezone

from gettogether.models import GetTogether
from travelingguestbook.factories import GetTogetherFactory


def test_get_together_str_method():
    """Test the __str__ method of the GetTogether model."""
    get_together = GetTogetherFactory(location="Test Location", date=timezone.now())
    expected_str = f"GetTogether at Test Location on {get_together.date} by {get_together.user.username}"
    assert str(get_together) == expected_str

class TestGetTogetherCreateView:
    """Test the GetTogether create view."""
    def test_get_together_create_view(self, auto_login_user):
        """Test the GetTogether create view to ensure it returns a 200 status code"""
        client, _ = auto_login_user()
        response = client.get(reverse('create-get-together'))
        assert response.status_code == 200
        assert response.template_name == ['gettogether/gettogether_form.html']

    def test_create_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the GetTogether create view."""
        response = client.get(reverse('create-get-together'))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_user_is_set_on_form_submission(self, auto_login_user):
        """Test that the user is set on the GetTogether instance upon form submission."""
        client, user = auto_login_user()
        response = client.post(reverse('create-get-together'), {
            'location': 'Test Location',
            'date': '2024-01-01 12:00:00'
        })
        assert response.status_code == 302
        get_together = GetTogether.objects.first()
        assert get_together.user == user

class TestGetTogetherUpdateView:
    """Test the GetTogether update view."""
    def test_update_by_same_user(self, auto_login_user):
        """Test the GetTogether update view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        gettogether = GetTogetherFactory(user=user)
        response = client.get(reverse('update-get-together', args=[gettogether.id]))
        assert response.status_code == 200
        assert response.template_name == ['gettogether/gettogether_form.html']

    def test_update_and_change_location(self, auto_login_user):
        """Test that a user can update the location of their own GetTogether instance."""
        client, user = auto_login_user()
        gettogether = GetTogetherFactory(user=user)
        new_location = 'Updated Location'
        response = client.post(reverse('update-get-together', args=[gettogether.id]), {
            'location': new_location,
            'date': gettogether.date
        })
        assert response.status_code == 302  # Redirect after successful update
        gettogether.refresh_from_db()
        assert gettogether.location == new_location

    def test_update_by_another_user(self, auto_login_user):
        """Test that a user different then the user who it is from,
        that user is not allowed to update that gettogehter"""
        client, _ = auto_login_user()
        gettogether = GetTogetherFactory()
        response = client.get(reverse('update-get-together', args=[gettogether.id]))
        assert response.status_code == 403  # Forbidden

    def test_not_logged_in(self, client):
        """Test that a user who is not logged in
        is redirected to the login page when trying to update a gettogether"""
        gettogether = GetTogetherFactory()
        response = client.get(reverse('update-get-together', args=[gettogether.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

class TestGetTogetherDeleteView:
    """Test the GetTogether delete view."""
    def test_success(self, auto_login_user):
        """Test the GetTogether delete view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        gettogether = GetTogetherFactory(user=user)
        response = client.post(reverse('delete-get-together', args=[gettogether.id]))
        assert response.status_code == 302
        assert GetTogether.objects.filter(id=gettogether.id).count() == 0  # Ensure the instance is deleted

    def test_delete_by_another_user(self, auto_login_user):
        """Test a user, different then the user who it is from,
        is not allowed to delete that gettogehter"""
        client, _ = auto_login_user()
        gettogether = GetTogetherFactory()
        response = client.post(reverse('delete-get-together', args=[gettogether.id]))
        assert response.status_code == 403  # Forbidden

    def test_not_logged_in(self, client):
        """Test a user, who is not logged in
        is redirected to the login page when trying to delete a gettogether"""
        gettogether = GetTogetherFactory()
        response = client.post(reverse('delete-get-together', args=[gettogether.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url
