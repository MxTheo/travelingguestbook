from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from streetactivity.models import Reflection
from travelingguestbook.factories import ReflectionFactory


class TestReflectionModel:
    """Tests for the Reflection model."""
    def test_reflection_str_method(self):
        """Test the __str__ method of the Reflection model returns the reflection"""
        expected_str = "Test123"
        reflection = ReflectionFactory(
            reflection=expected_str)
        returned_str = str(reflection)
        assert returned_str == expected_str+'... (Bluesky)'

    def test_reflection_str_method_no_reflection(self):
        """Test the __str__ method of the Reflection model when there is no reflection."""
        reflection = ReflectionFactory(reflection="")
        assert str(reflection) == "... (Bluesky)"


    def test_reflection_createview(self, client):
        """Test the Reflection create view for reflections"""
        create_url = reverse("create-reflection")

        reflection_data = create_reflection_data()

        response = client.post(create_url, reflection_data, follow=True)

        assert response.status_code == 200
        assert Reflection.objects.count() == 1

    def test_reflection_listview(self, client):
        """Test the Reflection list view for reflections"""
        ReflectionFactory.create_batch(2)

        list_url = reverse("reflection-list")
        response = client.get(list_url)

        assert response.status_code == 200
        assert "reflections" in response.context
        assert len(response.context["reflections"]) == 2

    def test_reflection_ordering(self):
        """Test that Reflection instances are ordered by date in descending order."""
        exp1 = ReflectionFactory(date_created=timezone.now() - timedelta(days=2))
        exp2 = ReflectionFactory(date_created=timezone.now() - timedelta(days=1))
        exp3 = ReflectionFactory(date_created=timezone.now())

        reflections = Reflection.objects.all()
        assert list(reflections) == [exp3, exp2, exp1]

    def test_delete_view(self, client):
        """Test the Reflection delete view for reflections"""
        reflection = ReflectionFactory()

        delete_reflection_url = reverse("delete-reflection", args=[reflection.id])

        response = client.post(delete_reflection_url)

        assert response.status_code == 302
        assert not Reflection.objects.filter(id=reflection.id).exists()
        assert Reflection.objects.count() == 0

    def test_reflection_missing_on_reflection_form(self, client):
        """Given the user forgets to fill in a reflection,
        test if the error 'Geen reflectie gegeven' is given"""
        create_url = reverse("create-reflection")
        reflection_data = create_reflection_data()
        reflection_data.pop("reflection", None)

        response = client.post(create_url, reflection_data)

        assert response.status_code == 200
        assert "Geen reflectie gegeven" in response.content.decode()


def create_reflection_data():
    """Helper function to create reflection data for tests."""
    reflection = ReflectionFactory.build()
    reflection_data = {
        "reflection": reflection.reflection,
    }
    return reflection_data
