from django.urls import reverse

from travelingguestbook.factories import LinkFactory
from weaktie.models import Link


def test_link_str_method():
    """Test the __str__ method of the Link model."""
    link = LinkFactory(url="https://example.com")
    expected_str = f"{link.user.username} link: {link.url}"
    assert str(link) == expected_str

class TestLinkCreateView:
    """Test the Link create view."""
    def test_link_create_view(self, auto_login_user):
        """Test the Link create view to ensure it returns a 200 status code"""
        client, _ = auto_login_user()
        response = client.get(reverse('create-link'))
        assert response.status_code == 200
        assert response.template_name == ['weaktie/link_form.html']

    def test_create_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the Link create view."""
        response = client.get(reverse('create-link'))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_user_is_set_on_form_submission(self, auto_login_user):
        """Test that the user is set on the Link instance upon form submission."""
        client, user = auto_login_user()
        response = client.post(reverse('create-link'), {
            'url': 'https://example.com'
        })
        assert response.status_code == 302
        link = Link.objects.first()
        assert link.user == user

class TestLinkUpdateView:
    """Test the Link update view."""
    def test_update_by_same_user(self, auto_login_user):
        """Test the Link update view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        link = LinkFactory(user=user)
        response = client.get(reverse('update-link', args=[link.id]))
        assert response.status_code == 200
        assert response.template_name == ['weaktie/link_form.html']

    def test_update_by_different_user(self, auto_login_user):
        """Test the Link update view to ensure it returns a 403 status code,
        when it is from a different user"""
        client, _ = auto_login_user()
        link = LinkFactory()  # Create a link with a different user
        response = client.get(reverse('update-link', args=[link.id]))
        assert response.status_code == 403

    def test_update_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the Link update view."""
        link = LinkFactory()
        response = client.get(reverse('update-link', args=[link.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_update_and_change_url(self, auto_login_user):
        """Test that a user can update the url of their own Link instance."""
        client, user = auto_login_user()
        link = LinkFactory(user=user)
        new_url = 'https://updated-example.com'
        response = client.post(reverse('update-link', args=[link.id]), {
            'url': new_url
        })
        assert response.status_code == 302
        link.refresh_from_db()
        assert link.url == new_url

class TestLinkDeleteView:
    """Test the Link delete view."""
    def test_delete_by_same_user(self, auto_login_user):
        """Test the Link delete view to ensure it returns a 200 status code,
        when it is from the same user"""
        client, user = auto_login_user()
        link = LinkFactory(user=user)
        response = client.get(reverse('delete-link', args=[link.id]))
        assert response.status_code == 200
        assert response.template_name == ['admin/confirm_delete.html']

    def test_delete_by_different_user(self, auto_login_user):
        """Test the Link delete view to ensure it returns a 403 status code,
        when it is from a different user"""
        client, _ = auto_login_user()
        link = LinkFactory()  # Create a link with a different user
        response = client.get(reverse('delete-link', args=[link.id]))
        assert response.status_code == 403

    def test_delete_not_logged_in(self, client):
        """Test that a user who is not logged in
          is redirected to the login page when trying to access the Link delete view."""
        link = LinkFactory()
        response = client.get(reverse('delete-link', args=[link.id]))
        assert response.status_code == 302  # Redirect to login page
        assert '/accounts/login/' in response.url

    def test_delete_link(self, auto_login_user):
        """Test that a user can delete their own Link instance."""
        client, user = auto_login_user()
        link = LinkFactory(user=user)
        response = client.post(reverse('delete-link', args=[link.id]))
        assert response.status_code == 302
        assert not Link.objects.filter(id=link.id).exists()