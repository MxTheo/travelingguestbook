from django.urls import reverse

from travelingguestbook.factories import ContactChannelFactory
from weaktie.models import ContactChannel


class TestContactChannelCreateView:
    """Test the ContactChannel create view."""
    def test_contactchannel_create_view(self, auto_login_user):
        """Test the ContactChannel create view to ensure it returns a 200 status code"""
        client, _ = auto_login_user()
        response = client.get(reverse('create-contactchannel'))
        assert response.status_code == 200
        assert response.template_name == ['weaktie/contactchannel_form.html']

    def test_create_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the ContactChannel create view."""
        response = client.get(reverse('create-contactchannel'))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_user_is_set_on_form_submission(self, auto_login_user):
        """Test that the user is set on the ContactChannel instance upon form submission."""
        client, user = auto_login_user()
        response = client.post(reverse('create-contactchannel'), {
            'url': 'https://example.com',
            'app': ContactChannel.App.SIGNAL,
        })
        assert response.status_code == 302
        contactchannel = ContactChannel.objects.first()
        assert contactchannel.user == user


class TestLinkDeleteView:
    """Test the ContactChannel delete view."""
    def test_delete_by_same_user(self, auto_login_user):
        """Test the ContactChannel delete view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        contactchannel = ContactChannelFactory(user=user)
        response = client.get(reverse('delete-contactchannel', args=[contactchannel.id]))
        assert response.status_code == 200
        assert response.template_name == ['admin/confirm_delete.html']

    def test_delete_by_different_user(self, auto_login_user):
        """Test the ContactChannel delete view to ensure it returns a 403 status code,
        when it is from a different user"""
        client, _ = auto_login_user()
        contactchannel = ContactChannelFactory()  # Create a link with a different user
        response = client.get(reverse('delete-contactchannel', args=[contactchannel.id]))
        assert response.status_code == 403

    def test_delete_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the ContactChannel delete view."""
        contactchannel = ContactChannelFactory()
        response = client.get(reverse('delete-contactchannel', args=[contactchannel.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_delete_link(self, auto_login_user):
        """Test that a user can delete their own ContactChannel instance."""
        client, user = auto_login_user()
        contactchannel = ContactChannelFactory(user=user)
        response = client.post(reverse('delete-contactchannel', args=[contactchannel.id]))
        assert response.status_code == 302
        assert not ContactChannel.objects.filter(id=contactchannel.id).exists()