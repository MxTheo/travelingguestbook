from django.urls import reverse

from streetactivity.models import StreetActivity
from streetactivity.views import StreetActivityDetailView
from travelingguestbook.factories import StreetActivityFactory, StreetActivityPhotoFactory


class TestStreetActivityModel:
    """Tests for the StreetActivity model."""
    def test_streetactivity_listview(self, client):
        """Test the StreetActivity list view to ensure it returns a 200 status code
        and contains the expected context."""
        StreetActivityFactory.create_batch(3)
        response = client.get(reverse("streetactivity-list"))
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
            "name": "Updated straatactiviteit",
            "description": activity.description,
            "method": activity.method,
            "question": activity.question,
            "supplies": activity.supplies
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        activity.refresh_from_db()
        assert activity.name == "Updated straatactiviteit"

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
        response = client.get(reverse("streetactivity-list"))
        assert response.status_code == 200

    def test_list_view_uses_correct_template(self, client):
        """Test that the list view uses the correct template"""
        response = client.get(reverse("streetactivity-list"))
        assert "streetactivity/streetactivity_list.html" in [
            t.name for t in response.templates
        ]

    def test_list_view_shows_activities(self, client):
        """Test that activities are displayed in the list view"""
        # Maak test straatactiviteiten aan met factory
        StreetActivityFactory(name="Test straatactiviteit 1")
        StreetActivityFactory(name="Test straatactiviteit 2")

        response = client.get(reverse("streetactivity-list"))
        content = response.content.decode()

        assert "Test straatactiviteit 1" in content
        assert "Test straatactiviteit 2" in content

    def test_list_view_pagination(self, client):
        """Test that pagination works correctly"""
        for i in range(15):
            StreetActivityFactory(name=f"Pagination Test {i}")

        response = client.get(reverse("streetactivity-list"))

        assert response.context["is_paginated"]
        assert len(response.context["activities"]) == 10

    def test_list_view_ordering(self, client):
        """Test that activities are ordered by name"""
        StreetActivityFactory(name="Zebra straatactiviteit")
        StreetActivityFactory(name="Alpha straatactiviteit")
        StreetActivityFactory(name="Beta straatactiviteit")

        response = client.get(reverse('streetactivity-list'))
        activities = list(response.context['activities'])

        names = [activity.name for activity in activities]
        assert names == sorted(names)

    def test_list_view_context_data(self, client):
        """Test that the correct context data is provided"""
        StreetActivityFactory()

        response = client.get(reverse("streetactivity-list"))
        context = response.context

        assert "activities" in context

class TestStreetActivityDetailView:
    """Tests for the StreetActivity detail view."""

    def test_detail_view_returns_200(self, client):
        """Test that the detail view returns a 200 status code"""
        activity = StreetActivityFactory()
        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        assert response.status_code == 200

    def test_detail_view_uses_correct_template(self, client):
        """Test that the detail view uses the correct template"""
        activity = StreetActivityFactory()
        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        assert "streetactivity/streetactivity_detail.html" in [
            t.name for t in response.templates
        ]

    def test_detail_view_shows_activity_details(self, client):
        """Test that activity details are displayed in the detail view"""
        activity = StreetActivityFactory(
            name="Detail Test straatactiviteit",
            description="Dit is een test beschrijving."
        )

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))

        assert "Detail Test straatactiviteit" in response.text
        assert "Dit is een test beschrijving" in response.text

    def test_detail_view_context_data(self, client):
        """Test that the correct context data is provided in the detail view"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert "activity" in context
        assert context["activity"] == activity

    def test_detail_view_reflection_statistics(self, client):
        """Test that reflection statistics are correctly calculated and included in context"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert "reflections_count" in context

    def test_detail_view_no_reflections(self, client):
        """Test that the detail view handles activities with no reflections gracefully"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert context["reflections_count"] == 0

    def test_negative_reflections_remaining(self, client):
        """Test if that when there are no reflections,
        then the reflections_remaining results in 0 and not -3"""
        activity = StreetActivityFactory()
        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context
        assert context['reflections_remaining'] == 0

    def test_random_photo(self, temporary_media_root):
        """Given an activity with 2 photo's,
        test that it returns a photo
        """
        activity = StreetActivityFactory()
        StreetActivityPhotoFactory(activity=activity)
        StreetActivityPhotoFactory(activity=activity)

        view = StreetActivityDetailView()
        random_photo = view.get_random_photo(activity)
        assert random_photo is not None

    def test_no_photo(self):
        """Given an activity with no photo's,
        test that it returns no photo"""
        activity = StreetActivityFactory()
        
        view = StreetActivityDetailView()
        random_photo = view.get_random_photo(activity)
        assert random_photo is None