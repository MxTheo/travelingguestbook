from django.urls import reverse
from freezegun import freeze_time
from travelingguestbook.factories import ExperienceFactory, StreetActivityFactory, MomentFactory
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

    def test_add_moment_data_to_context(self, auto_login_user):
        """Test that the moment_data is created in json format of the Experience detail view"""
        client, user = auto_login_user()
        experience = ExperienceFactory(user=user)
        MomentFactory(
            experience=experience,
            report="Test report",
        )
        detail_url = reverse("experience-detail", kwargs={"pk": experience.id})

        response = client.get(detail_url)

        assert response.status_code == 200
        moment_data_json = response.context["moments_json"]
        assert '"report": "Test report"' in moment_data_json


class TestAddMomentToExperienceFlow:
    """Test the full flow of adding moments to experience"""
    def test_add_first_moment_to_experience(self, auto_login_user):
        """
        Test the full flow of adding the first moment to a new experience:
        1. Post moment data without activity.
        2. Select an activity.
        3. Assign activity and save the moment.
        Verify that a new experience and moment are created.
        """
        client, _ = auto_login_user()
        activity = StreetActivityFactory()
        url_add_first = reverse('add-first-moment-to-experience')

        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        self.post_moment_data(client, url_add_first, moment_data)

        self.post_select_activity(client, activity)

        response = self.get_assign_activity(client)

        # Verify database state
        experience = Experience.objects.first()
        moment = Moment.objects.first()

        assert experience is not None
        assert moment is not None
        assert moment.experience == experience
        assert moment.activity == activity
        assert moment.report == moment_data['report']
        assert response.url == reverse('experience-detail', kwargs={'pk': experience.id})

    def test_add_second_moment_to_experience(self, auto_login_user):
        """
        Test the full flow of adding a second moment to an existing experience:
        1. Post moment data with existing experience_id.
        2. Select a new activity.
        3. Assign activity and save the moment.
        Verify that no new experience is created and the moment count increases.
        """
        client, user = auto_login_user()

        experience = ExperienceFactory(user=user)
        MomentFactory(experience=experience)
        activity_new_moment = StreetActivityFactory()

        url_add_moment = reverse('add-moment-to-experience',
                                 kwargs={'experience_id': experience.id})
        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        self.post_moment_data(client, url_add_moment, moment_data)

        self.post_select_activity(client, activity_new_moment)

        response = self.get_assign_activity(client)

        # Verify database state
        assert Experience.objects.count() == 1  # No new experience
        assert Moment.objects.filter(experience=experience).count() == 2

        second_moment = Moment.objects.filter(experience=experience).order_by('-order').first()
        assert second_moment.activity == activity_new_moment
        assert second_moment.report == moment_data['report']
        assert response.url == reverse('experience-detail', kwargs={'pk': experience.id})

    def post_moment_data(self, client, url, moment_data):
        """Post moment form data without activity to start the flow."""
        response = client.post(url, data=moment_data)
        assert response.status_code == 302
        assert response.url == reverse('select-activity-for-moment')
        return response

    def post_select_activity(self, client, activity):
        """Post selected activity to session and redirect to assign moment."""
        url = reverse('select-activity-for-moment')
        response = client.post(url, data={'activity_id': str(activity.id)})
        assert response.status_code == 302
        assert response.url == reverse('assign-activity-to-moment')
        return response

    def get_assign_activity(self, client):
        """Perform GET request to assign activity and save moment."""
        url = reverse('assign-activity-to-moment')
        response = client.get(url)
        assert response.status_code == 302
        return response

    def test_missing_report(self, auto_login_user):
        """Given no report is filled in,
        test if the user is redirected back to the form
        and gets an error"""
        client, _ = auto_login_user()
        url_add_first = reverse('add-first-moment-to-experience')
        moment_data = create_moment_data()
        moment_data['report'] = '' # Remove report to simulate missing input
        moment_data.pop('activity', None)
        response = client.post(url_add_first, data=moment_data)
        assert response.status_code == 200
        errors = response.context['form'].errors
        assert 'report' in errors

    def test_missing_keywords(self, auto_login_user):
        """Given no keywords entered,
        test if the user is redirected back to the form
        and gets an error"""
        client, _ = auto_login_user()
        url_add_first = reverse('add-first-moment-to-experience')
        moment_data = create_moment_data()
        moment_data['keywords'] = '' # Remove keywords to simulate missing input
        moment_data.pop('activity', None)
        response = client.post(url_add_first, data=moment_data)
        assert response.status_code == 200  # Form re-rendered
        errors = response.context['form'].errors
        assert 'keywords' in errors

    def test_missing_report_and_keywords(self, auto_login_user):
        """Given no keywords and no report entered,
        test if the user is redirected back to the form
        and gets errors"""
        client, _ = auto_login_user()
        url_add_first = reverse('add-first-moment-to-experience')
        moment_data = create_moment_data()
        moment_data['keywords'] = '' # Remove keywords to simulate missing input
        moment_data['report'] = '' # Remove report to simulate missing input
        moment_data.pop('activity', None)
        response = client.post(url_add_first, data=moment_data)
        assert response.status_code == 200  # Form re-rendered
        errors = response.context['form'].errors
        assert 'keywords' in errors
        assert 'report' in errors

    def test_updating_moment_data_when_going_back_to_moment_form(self, auto_login_user):
        """
        Given there is already moment data present,
        for example when the user goes back to the form,
        test that the initial values from the session are given
        """
        client, _ = auto_login_user()
        url_add_first = reverse('add-first-moment-to-experience')
        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        # First post to set session data
        response = client.post(url_add_first, data=moment_data)
        assert response.status_code == 302
        assert response.url == reverse('select-activity-for-moment')

        # Now go back to the moment form
        response = client.get(url_add_first)
        assert response.status_code == 200

        form = response.context['form']
        for field, value in moment_data.items():
            assert form.initial[field] == value
