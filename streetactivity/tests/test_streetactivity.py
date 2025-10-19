from django.urls import reverse
from streetactivity.models import StreetActivity
from travelingguestbook.factories import StreetActivityFactory

class TestStreetActivityModel:
    """Tests for the StreetActivity model."""
    def test_streetactivity_listview(self, client):
        """Test the StreetActivity list view to ensure it returns a 200 status code
        and contains the expected context."""
        StreetActivityFactory.create_batch(3)
        response = client.get(reverse("streetactivity_list"))
        assert response.status_code == 200
        assert "activities" in response.context
        assert len(response.context["activities"]) == 3

    def test_streetactivity_createview(self, client):
        """Test the StreetActivity create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        create_url = reverse("create-streetactivity")

        activity_data = StreetActivityFactory.build().__dict__
        for field in ["_state", "id"]:
            activity_data.pop(field, None)

        response = client.post(create_url, activity_data, follow=True)

        assert response.status_code == 200
        assert StreetActivity.objects.count() == 1

    def test_streetactivity_updateview(self, client):
        """Test the StreetActivity update view to ensure it returns a 200 status code
        and contains the expected form in context."""
        activity = StreetActivityFactory()
        update_url = reverse("update-streetactivity", args=[activity.id])

        updated_data = {
            "name": "Updated Activiteit",
            "description": activity.description,
            "method": activity.method,
            "question": activity.question,
            "supplies": activity.supplies
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        activity.refresh_from_db()
        assert activity.name == "Updated Activiteit"

    def test_streetactivity_deleteview(self, client):
        """Test the StreetActivity delete view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()

        assert StreetActivity.objects.filter(id=activity.id).exists()

        delete_streetactivity_url = reverse("delete-streetactivity", args=[activity.id])

        response = client.post(delete_streetactivity_url)

        assert response.status_code == 302
        assert not StreetActivity.objects.filter(id=activity.id).exists()
        assert StreetActivity.objects.count() == 0

    def test_streetactivity_string(self):
        """Test string reprensentation of streetactivity"""
        activity = StreetActivityFactory(name="test")
        assert str(activity) == "test"

class TestStreetActivityListView:
    """Tests for the StreetActivity list view."""

    def test_list_view_returns_200(self, client):
        """Test that the list view returns a 200 status code"""
        response = client.get(reverse("streetactivity_list"))
        assert response.status_code == 200

    def test_list_view_uses_correct_template(self, client):
        """Test that the list view uses the correct template"""
        response = client.get(reverse("streetactivity_list"))
        assert "streetactivity/streetactivity_list.html" in [
            t.name for t in response.templates
        ]

    def test_list_view_shows_activities(self, client):
        """Test that activities are displayed in the list view"""
        # Maak test activiteiten aan met factory
        StreetActivityFactory(name="Test Activiteit 1")
        StreetActivityFactory(name="Test Activiteit 2")

        response = client.get(reverse("streetactivity_list"))
        content = response.content.decode()

        assert "Test Activiteit 1" in content
        assert "Test Activiteit 2" in content

    def test_list_view_pagination(self, client):
        """Test that pagination works correctly"""
        for i in range(15):
            StreetActivityFactory(name=f"Pagination Test {i}")

        response = client.get(reverse("streetactivity_list"))

        assert response.context["is_paginated"]
        assert len(response.context["activities"]) == 10

    def test_list_view_ordering(self, client):
        """Test that activities are ordered by name"""
        StreetActivityFactory(name="Zebra Activiteit")
        StreetActivityFactory(name="Alpha Activiteit")
        StreetActivityFactory(name="Beta Activiteit")

        response = client.get(reverse('streetactivity_list'))
        activities = list(response.context['activities'])

        names = [activity.name for activity in activities]
        assert names == sorted(names)

    def test_list_view_context_data(self, client):
        """Test that the correct context data is provided"""
        StreetActivityFactory()

        response = client.get(reverse("streetactivity_list"))
        context = response.context

        assert "activities" in context
