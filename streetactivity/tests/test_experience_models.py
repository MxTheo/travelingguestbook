from django.urls import reverse
from django.core.exceptions import ValidationError
from travelingguestbook.factories import ExperienceFactory, StreetActivityFactory
from streetactivity.models import Experience


class TestExperienceModel:
    """Tests for the Experience model."""
    def test_experience_str_method(self):
        """Test the __str__ method of the Experience model to ensure it returns
        the first 50 characters of the report followed by ellipsis."""
        experience = ExperienceFactory(
            report="This is a test report for the experience model. It should be truncated.")
        expected_str = "This is a test report for the experience model. It..."
        assert str(experience) == expected_str

    def test_experience_str_method_no_report(self):
        """Test the __str__ method of the Experience model when there is no report."""
        activity = StreetActivityFactory(name="Test Activity")
        experience = ExperienceFactory(activity=activity, report="")
        expected_str = f"{activity.name} - Ervaring {experience.id}"
        assert str(experience) == expected_str

    def test_experience_createview_leads_for_form_from_passerby(self, client):
        """Test the Experience create view for passerby to ensure it
        returns a 200 status code and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience-from-passerby", args=[activity.id])
        response = client.get(create_url)
        assert response.status_code == 200
        assert "Ervaring als Voorbijganger" in response.content.decode()

    def test_experience_createview(self, client):
        """Test the Experience create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience", args=[activity.id])

        experience_data = ExperienceFactory.build().__dict__
        for field in ["_state", "id", 'activity_id']:
            experience_data.pop(field, None)

        response = client.post(create_url, experience_data, follow=True)

        assert response.status_code == 200
        assert Experience.objects.count() == 1

    def test_experience_createview_from_practitioner(self, client):
        """Test the Experience create view for practitioners to ensure it
        returns a 200 status code and sets from_practitioner to True."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience-from-practitioner", args=[activity.id])
        experience_data = ExperienceFactory.build().__dict__
        for field in ["_state", "id", 'activity_id']:
            experience_data.pop(field, None)
        response = client.post(create_url, experience_data, follow=True)
        assert response.status_code == 200
        assert Experience.objects.count() == 1
        experience = Experience.objects.first()
        assert experience.from_practitioner

    def test_experience_createview_from_passerby(self, client):
        """Test the Experience create view for passerby to ensure it
        returns a 200 status code and sets from_practitioner to False."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience-from-passerby", args=[activity.id])
        experience_data = ExperienceFactory.build().__dict__
        for field in ["_state", "id", 'activity_id']:
            experience_data.pop(field, None)
        response = client.post(create_url, experience_data, follow=True)
        assert response.status_code == 200
        assert Experience.objects.count() == 1
        experience = Experience.objects.first()
        assert not experience.from_practitioner

    def test_experience_listview(self, client):
        """Test the Experience list view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()
        for _ in range(3):
            ExperienceFactory(activity=activity)
        response = client.get(reverse("experience-list-streetactivity", args=[activity.id]))
        assert response.status_code == 200
        assert "experiences" in response.context
        assert len(response.context["experiences"]) == 3

    def test_experience_listview_by_streetactivity(self, client):
        """Test the Experience list view filtered by StreetActivity to ensure it
        returns a 200 status code and contains the expected context."""
        activity = StreetActivityFactory()
        ExperienceFactory.create_batch(2, activity=activity)
        ExperienceFactory.create_batch(2)  # Experiences for other activities

        list_url = reverse("experience-list-streetactivity", args=[activity.id])
        response = client.get(list_url)

        assert response.status_code == 200
        assert "experiences" in response.context
        assert len(response.context["experiences"]) == 2
        for experience in response.context["experiences"]:
            assert experience.activity == activity

    def test_experience_ordering(self):
        """Test that Experience instances are ordered by date in descending order."""
        exp1 = ExperienceFactory(date_created="2023-01-01")
        exp2 = ExperienceFactory(date_created="2023-02-01")
        exp3 = ExperienceFactory(date_created="2023-03-01")

        experiences = Experience.objects.all()
        assert list(experiences) == [exp3, exp2, exp1]

    def test_experience_activity_relationship(self):
        """Test the ForeignKey relationship between Experience and StreetActivity."""
        activity = StreetActivityFactory()
        experience = ExperienceFactory(activity=activity)

        assert experience.activity == activity
        assert experience in activity.experiences.all()