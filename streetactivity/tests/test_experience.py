from django.urls import reverse
from travelingguestbook.factories import MomentFactory, StreetActivityFactory, ExperienceFactory
from streetactivity.models import Moment, Experience
from freezegun import freeze_time

class TestExperience:
    """Tests for the Experience model."""

    @freeze_time("01-01-2024 00:00")
    def test_experience_str_method(self):
        """Test the __str__ method of the Experience model to ensure it returns
        the expected string representation."""
        experience = ExperienceFactory()
        expected_str = "Ervaring 01-01-2024 00:00"
        returned_str = str(experience)
        assert returned_str == expected_str

    def test_experience_createview(self, auto_login_user):
        """Test the Experience create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        client, user = auto_login_user()
        create_url = reverse("create-experience")

        response = client.post(create_url, follow=True)

        assert response.status_code == 200
        assert Experience.objects.count() == 1
        experience = Experience.objects.first()
        assert experience.user == user

    def test_experience_delete(self, auto_login_user):
        """Test the Experience delete view to ensure it deletes the experience
        and redirects to the expected URL."""
        client, user = auto_login_user()
        experience = ExperienceFactory(user=user)
        delete_url = reverse("delete-experience", kwargs={"pk": experience.id})

        response = client.post(delete_url, follow=True)

        assert response.status_code == 200
        assert Experience.objects.count() == 0
        assert response.redirect_chain[0][0] == reverse("user", kwargs={"username": user.username})