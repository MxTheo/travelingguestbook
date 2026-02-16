from django.urls import reverse
from travelingguestbook.factories import MomentFactory, StreetActivityFactory
from streetactivity.models import Moment


class TestMomentModel:
    """Tests for the Moment model."""
    def test_moment_str_method(self):
        """Test the __str__ method of the Moment model to ensure it returns
        the first 50 characters of the report followed by ellipsis."""
        moment = MomentFactory(
            report="This is a test report for the moment model. It should be truncated.")
        expected_str = "This is a test report for the moment model. It sho..."
        returned_str = str(moment)
        assert returned_str == expected_str

    def test_moment_str_method_no_report(self):
        """Test the __str__ method of the Moment model when there is no report."""
        activity = StreetActivityFactory(name="Test Activity")
        moment = MomentFactory(activity=activity, report="")
        expected_str = f"{activity.name} - Moment {moment.id}"
        assert str(moment) == expected_str

    def test_moment_createview_leads_for_form_from_passerby(self, client):
        """Test the Moment create view for passerby to ensure it
        returns a 200 status code and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-moment-from-passerby", args=[activity.id])
        response = client.get(create_url)
        assert response.status_code == 200
        assert "Moment als Voorbijganger" in response.content.decode()

    def test_moment_createview(self, client):
        """Test the Moment create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-moment-from-practitioner", args=[activity.id])

        moment_data = create_moment_data(activity)

        response = client.post(create_url, moment_data, follow=True)

        assert response.status_code == 200
        assert Moment.objects.count() == 1

    def test_moment_createview_from_practitioner(self, client):
        """Test the Moment create view for practitioners to ensure it
        returns a 200 status code and sets from_practitioner to True."""
        activity = StreetActivityFactory()
        create_url = reverse("create-moment-from-practitioner", args=[activity.id])
        moment_data = create_moment_data(activity)
        response = client.post(create_url, moment_data, follow=True)
        assert response.status_code == 200
        assert Moment.objects.count() == 1
        moment = Moment.objects.first()  # type: ignore[reportOptionalMemberAccess]
        assert moment.from_practitioner  # type: ignore[reportOptionalMemberAccess]

    def test_moment_createview_from_passerby(self, client):
        """Test the Moment create view for passerby to ensure it
        returns a 200 status code and sets from_practitioner to False."""
        activity = StreetActivityFactory()
        create_url = reverse("create-moment-from-passerby", args=[activity.id])
        moment_data = create_moment_data(activity)
        response = client.post(create_url, moment_data, follow=True)
        assert response.status_code == 200
        assert Moment.objects.count() == 1
        moment = Moment.objects.first()  # type: ignore[reportOptionalMemberAccess]
        assert not moment.from_practitioner  # type: ignore[reportOptionalMemberAccess]

    def test_moment_listview(self, client):
        """Test the Moment list view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()
        for _ in range(3):
            MomentFactory(activity=activity)
        response = client.get(reverse("moment-list-streetactivity", args=[activity.id]))
        assert response.status_code == 200
        assert "moments" in response.context
        assert len(response.context["moments"]) == 3

    def test_moment_listview_by_streetactivity(self, client):
        """Test the Moment list view filtered by StreetActivity to ensure it
        returns a 200 status code and contains the expected context."""
        activity = StreetActivityFactory()
        MomentFactory.create_batch(2, activity=activity)
        MomentFactory.create_batch(2)  # Moments for other activities

        list_url = reverse("moment-list-streetactivity", args=[activity.id])
        response = client.get(list_url)

        assert response.status_code == 200
        assert "moments" in response.context
        assert len(response.context["moments"]) == 2
        for moment in response.context["moments"]:
            assert moment.activity == activity

    def test_moment_ordering(self):
        """Test that Moment instances are ordered by date in descending order."""
        exp1 = MomentFactory(date_created="2023-01-01")
        exp2 = MomentFactory(date_created="2023-02-01")
        exp3 = MomentFactory(date_created="2023-03-01")

        moments = Moment.objects.all()
        assert list(moments) == [exp3, exp2, exp1]

    def test_moment_activity_relationship(self):
        """Test the ForeignKey relationship between Moment and StreetActivity."""
        activity = StreetActivityFactory()
        moment = MomentFactory(activity=activity)

        assert moment.activity == activity
        assert moment in activity.moments.all()

    def test_delete_view(self, client):
        """Test the Moment delete view to ensure it returns a 200 status code
        and contains the expected context."""
        moment = MomentFactory()

        delete_moment_url = reverse("delete-moment", args=[moment.id])

        response = client.post(delete_moment_url)

        assert response.status_code == 302
        assert not Moment.objects.filter(id=moment.id).exists()
        assert Moment.objects.count() == 0

    def test_update_view(self, client):
        """Test the Moment update view to ensure it returns a 200 status code
        and contains the expected form in context."""
        moment = MomentFactory()
        update_url = reverse("update-moment", args=[moment.id])

        updated_data = {
            "report": "Updated Moment",
            "activity": moment.activity,
            "confidence_level": moment.confidence_level,
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        moment.refresh_from_db()
        assert moment.report == "Updated Moment"

    def test_updateview_practitioner(self, client):
        """Given an moment from a practitioner, test that the form shows Moment als Beoefenaar"""
        moment = MomentFactory(from_practitioner=True)
        update_url = reverse("update-moment", args=[moment.id])

        response = client.get(update_url)

        assert "Moment als Beoefenaar" in response.content.decode()

def create_moment_data(activity=None):
    """Helper function to create moment data for tests."""
    if not activity:
        activity = StreetActivityFactory()
    moment_data = MomentFactory.build().__dict__
    for field in [
        "_state",
        "id",
        'activity_id',
        'experience_id',
        'from_practitioner',
        'date_created', 'date_modified',
        'order']:
        moment_data.pop(field, None)
    moment_data['activity'] = activity.id
    moment_data['confidence_level'] = str(moment_data.get('confidence_level', 3))
    return moment_data
