from django.urls import reverse
from django.utils import timezone

from weaktie.models import Whereabout
from travelingguestbook.factories import WhereaboutFactory


def test_get_together_str_method():
    """Test the __str__ method of the Whereabout model."""
    get_together = WhereaboutFactory(location="Test Location", date=timezone.now())
    expected_str = f"Whereabout at Test Location on {get_together.date} by {get_together.user.username}"
    assert str(get_together) == expected_str

class TestWhereaboutCreateView:
    """Test the Whereabout create view."""
    def test_get_together_create_view(self, auto_login_user):
        """Test the Whereabout create view to ensure it returns a 200 status code"""
        client, _ = auto_login_user()
        response = client.get(reverse('create-get-together'))
        assert response.status_code == 200
        assert response.template_name == ['whereabout/whereabout_form.html']

    def test_create_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the Whereabout create view."""
        response = client.get(reverse('create-get-together'))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_user_is_set_on_form_submission(self, auto_login_user):
        """Test that the user is set on the Whereabout instance upon form submission."""
        client, user = auto_login_user()
        response = client.post(reverse('create-get-together'), {
            'location': 'Test Location',
            'date': '2024-01-01 12:00:00'
        })
        assert response.status_code == 302
        get_together = Whereabout.objects.first()
        assert get_together.user == user

class TestWhereaboutUpdateView:
    """Test the Whereabout update view."""
    def test_update_by_same_user(self, auto_login_user):
        """Test the Whereabout update view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        whereabout = WhereaboutFactory(user=user)
        response = client.get(reverse('update-get-together', args=[whereabout.id]))
        assert response.status_code == 200
        assert response.template_name == ['whereabout/whereabout_form.html']

    def test_update_and_change_location(self, auto_login_user):
        """Test that a user can update the location of their own Whereabout instance."""
        client, user = auto_login_user()
        whereabout = WhereaboutFactory(user=user)
        new_location = 'Updated Location'
        response = client.post(reverse('update-get-together', args=[whereabout.id]), {
            'location': new_location,
            'date': whereabout.date
        })
        assert response.status_code == 302  # Redirect after successful update
        whereabout.refresh_from_db()
        assert whereabout.location == new_location

    def test_update_by_another_user(self, auto_login_user):
        """Test that a user different then the user who it is from,
        that user is not allowed to update that gettogehter"""
        client, _ = auto_login_user()
        whereabout = WhereaboutFactory()
        response = client.get(reverse('update-get-together', args=[whereabout.id]))
        assert response.status_code == 403  # Forbidden

    def test_not_logged_in(self, client):
        """Test that a user who is not logged in
        is redirected to the login page when trying to update a whereabout"""
        whereabout = WhereaboutFactory()
        response = client.get(reverse('update-get-together', args=[whereabout.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

class TestWhereaboutDeleteView:
    """Test the Whereabout delete view."""
    def test_success(self, auto_login_user):
        """Test the Whereabout delete view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        whereabout = WhereaboutFactory(user=user)
        response = client.post(reverse('delete-get-together', args=[whereabout.id]))
        assert response.status_code == 302
        assert Whereabout.objects.filter(id=whereabout.id).count() == 0  # Ensure the instance is deleted

    def test_delete_by_another_user(self, auto_login_user):
        """Test a user, different then the user who it is from,
        is not allowed to delete that gettogehter"""
        client, _ = auto_login_user()
        whereabout = WhereaboutFactory()
        response = client.post(reverse('delete-get-together', args=[whereabout.id]))
        assert response.status_code == 403  # Forbidden

    def test_not_logged_in(self, client):
        """Test a user, who is not logged in
        is redirected to the login page when trying to delete a whereabout"""
        whereabout = WhereaboutFactory()
        response = client.post(reverse('delete-get-together', args=[whereabout.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url
