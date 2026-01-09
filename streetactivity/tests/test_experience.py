from django.urls import reverse
from freezegun import freeze_time
from travelingguestbook.factories import ExperienceFactory
from streetactivity.tests.test_moment_models import create_moment_data
from streetactivity.models import Moment, Experience

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

    def test_start_experience_view(self, auto_login_user):
        """Test the Start Experience view to ensure it returns a 200 status code
        and contains the expected form in context."""
        client, _ = auto_login_user()
        start_url = reverse("start-experience")

        response = client.get(start_url)

        assert response.status_code == 200
        assert "Ervaring Starten" in response.content.decode()
        assert Experience.objects.count() == 0  # No experience created yet

    def test_that_no_experience_is_created_when_first_moment_is_not_finished(self, auto_login_user):
        """Test that no experience is created when the first moment form
        is accessed but not submitted."""
        client, _ = auto_login_user()
        add_moment_url = reverse("add-first-moment-to-experience")
        response = client.get(add_moment_url)
        assert response.status_code == 200
        assert Experience.objects.count() == 0

    def test_add_first_moment_to_experience(self, auto_login_user):
        """Test adding the first moment when there is no experience
        creates a new experience and associates the moment with it."""
        client, user = auto_login_user()
        add_moment_url = reverse("add-first-moment-to-experience")
        moment_data = create_moment_data()

        response = client.post(add_moment_url, data=moment_data, follow=True)

        assert response.status_code == 200
        assert Experience.objects.count() == 1
        experience = Experience.objects.first()  # type: ignore[reportOptionalMemberAccess]
        assert experience.user == user  # type: ignore[reportOptionalMemberAccess]
        assert Moment.objects.count() == 1
        moment = Moment.objects.first()  # type: ignore[reportOptionalMemberAccess]
        assert moment.experience == experience  # type: ignore[reportOptionalMemberAccess]

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
