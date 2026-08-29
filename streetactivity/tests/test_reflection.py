from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from streetactivity.models import Reflection
from travelingguestbook.factories import ReflectionFactory, StreetActivityFactory


class TestReflectionModel:
    """Tests for the Reflection model."""
    def test_reflection_str_method(self):
        """Test the __str__ method of the Reflection model returns the reflection"""
        expected_str = "Test123"
        reflection = ReflectionFactory(
            reflection=expected_str)
        returned_str = str(reflection)
        assert returned_str == expected_str

    def test_reflection_str_method_no_reflection(self):
        """Test the __str__ method of the Reflection model when there is no reflection."""
        activity = StreetActivityFactory(name="Test Activity")
        reflection = ReflectionFactory(activity=activity, reflection="")
        assert str(reflection) == ""

    def test_reflection_createview(self, client):
        """Test the Reflection create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-reflection-activity", args=[activity.id])

        reflection_data = create_reflection_data(activity)

        response = client.post(create_url, reflection_data, follow=True)

        assert response.status_code == 200
        assert Reflection.objects.count() == 1

    def test_reflection_createview_no_activity(self, client):
        """Test the Reflection create view for reflections not linked to any StreetActivity."""
        create_url = reverse("create-reflection-no-activity")

        reflection_data = create_reflection_data(activity=None)

        response = client.post(create_url, reflection_data, follow=True)

        assert response.status_code == 200
        assert Reflection.objects.count() == 1

    def test_reflection_listview(self, client):
        """Test the Reflection list view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()
        for _ in range(3):
            ReflectionFactory(activity=activity)
        response = client.get(reverse("reflection-list-activity", args=[activity.id]))
        assert response.status_code == 200
        assert "reflections" in response.context
        assert len(response.context["reflections"]) == 3

    def test_reflection_listview_by_streetactivity(self, client):
        """Test the Reflection list view filtered by StreetActivity to ensure it
        returns a 200 status code and contains the expected context."""
        activity = StreetActivityFactory()
        ReflectionFactory.create_batch(2, activity=activity)
        ReflectionFactory.create_batch(2)  # Reflections for other activities

        list_url = reverse("reflection-list-activity", args=[activity.id])
        response = client.get(list_url)

        assert response.status_code == 200
        assert "reflections" in response.context
        assert len(response.context["reflections"]) == 2
        for reflection in response.context["reflections"]:
            assert reflection.activity == activity

    def test_reflection_listview_loose(self, client):
        """Test the Reflection list view for reflections not linked to any StreetActivity."""
        ReflectionFactory.create_batch(2, activity=None)
        ReflectionFactory.create_batch(2, activity=StreetActivityFactory())  # Linked reflections

        list_url = reverse("reflection-list-no-activity")
        response = client.get(list_url)

        assert response.status_code == 200
        assert "reflections" in response.context
        assert len(response.context["reflections"]) == 2
        for reflection in response.context["reflections"]:
            assert reflection.activity is None

    def test_reflection_ordering(self):
        """Test that Reflection instances are ordered by date in descending order."""
        exp1 = ReflectionFactory(date_created=timezone.now() - timedelta(days=2))
        exp2 = ReflectionFactory(date_created=timezone.now() - timedelta(days=1))
        exp3 = ReflectionFactory(date_created=timezone.now())

        reflections = Reflection.objects.all()
        assert list(reflections) == [exp3, exp2, exp1]

    def test_reflection_activity_relationship(self):
        """Test the ForeignKey relationship between Reflection and StreetActivity."""
        activity = StreetActivityFactory()
        reflection = ReflectionFactory(activity=activity)

        assert reflection.activity == activity
        assert reflection in activity.reflections.all()

    def test_delete_view(self, client):
        """Test the Reflection delete view to ensure it returns a 200 status code
        and contains the expected context."""
        reflection = ReflectionFactory()

        delete_reflection_url = reverse("delete-reflection", args=[reflection.id])

        response = client.post(delete_reflection_url)

        assert response.status_code == 302
        assert not Reflection.objects.filter(id=reflection.id).exists()
        assert Reflection.objects.count() == 0

    def test_update_view(self, client):
        """Test the Reflection update view to ensure it returns a 200 status code
        and contains the expected form in context."""
        reflection = ReflectionFactory()
        update_url = reverse("update-reflection", args=[reflection.id])

        updated_data = {
            "reflection": "Updated",
            "activity": reflection.activity,
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        reflection.refresh_from_db()
        assert reflection.reflection == "Updated"

    def test_get_context_data_reflection_createview(self, client):
        """Given the user creates a reflection,
        test if activity is in the context"""
        activity = StreetActivityFactory()
        create_url = reverse("create-reflection-activity", args=[activity.id])
        response = client.get(create_url)
        assert response.status_code == 200
        assert "activity" in response.context

    def test_get_context_data_reflection_updateview(self, client):
        """Given the user updates a reflection,
        test if activity is in the context"""
        reflection = ReflectionFactory()
        update_url = reverse("update-reflection", args=[reflection.id])
        response = client.get(update_url)
        assert response.status_code == 200
        assert "activity" in response.context

    def test_reflection_missing_on_reflection_form(self, client):
        """Given the user forgets to fill in a reflection,
        test if the error 'Geen reflectie gegeven' is given"""
        activity = StreetActivityFactory()
        create_url = reverse("create-reflection-activity", args=[activity.id])
        reflection_data = create_reflection_data(activity)
        reflection_data.pop("reflection", None)

        response = client.post(create_url, reflection_data)

        assert response.status_code == 200
        assert "Geen reflectie gegeven" in response.content.decode()


def create_reflection_data(activity=None):
    """Helper function to create reflection data for tests."""
    reflection_data = ReflectionFactory.build().__dict__
    for field in [
        "_state",
        "id",
        'activity_id',
        'user_id',
        'date_created', 'date_modified']:
        reflection_data.pop(field, None)
    if activity:
        reflection_data['activity'] = activity.id
    return reflection_data
