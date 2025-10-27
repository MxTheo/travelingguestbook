from django.urls import reverse
from streetactivity.models import StreetActivity, Tag, Experience
from travelingguestbook.factories import ExperienceFactory, StreetActivityFactory

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
        # Maak test activiteiten aan met factory
        StreetActivityFactory(name="Test Activiteit 1")
        StreetActivityFactory(name="Test Activiteit 2")

        response = client.get(reverse("streetactivity-list"))
        content = response.content.decode()

        assert "Test Activiteit 1" in content
        assert "Test Activiteit 2" in content

    def test_list_view_pagination(self, client):
        """Test that pagination works correctly"""
        for i in range(15):
            StreetActivityFactory(name=f"Pagination Test {i}")

        response = client.get(reverse("streetactivity-list"))

        assert response.context["is_paginated"]
        assert len(response.context["activities"]) == 10

    def test_list_view_ordering(self, client):
        """Test that activities are ordered by name"""
        StreetActivityFactory(name="Zebra Activiteit")
        StreetActivityFactory(name="Alpha Activiteit")
        StreetActivityFactory(name="Beta Activiteit")

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
            name="Detail Test Activiteit",
            description="Dit is een test beschrijving."
        )

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))

    def test_detail_view_context_data(self, client):
        """Test that the correct context data is provided in the detail view"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert "activity" in context
        assert context["activity"] == activity

    def test_detail_view_experience_statistics(self, client):
        """Test that experience statistics are correctly calculated and included in context"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert "experiences_count" in context
        assert "practitioner_count" in context
        assert "passerby_count" in context
        assert "chart_data_everyone" in context
        assert "chart_data_practitioners" in context
        assert "chart_data_passersby" in context
        assert "tag_data_everyone" in context
        assert "tag_data_practitioners" in context
        assert "tag_data_passersby" in context
        assert "all_tags" in context

    def test_detail_view_no_experiences(self, client):
        """Test that the detail view handles activities with no experiences gracefully"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert context["experiences_count"] == 0
        assert context["practitioner_count"] == 0
        assert context["passerby_count"] == 0
        assert context["chart_data_everyone"] == {'pioneer': 0, 'intermediate': 0, 'climax': 0}
        assert context["chart_data_practitioners"] == {'pioneer': 0, 'intermediate': 0, 'climax': 0}
        assert context["chart_data_passersby"] == {'pioneer': 0, 'intermediate': 0, 'climax': 0}
        assert context["tag_data_everyone"] == []
        assert context["tag_data_practitioners"] == []
        assert context["tag_data_passersby"] == []
        assert list(context["all_tags"]) == []

    def test_detail_view_with_experiences(self, client):
        """Test that the detail view correctly calculates statistics with experiences present"""

        activity = StreetActivityFactory()

        tag1 = Tag.objects.create(name="Tag1", nvc_category="Category1")
        tag2 = Tag.objects.create(name="Tag2", nvc_category="Category2")

        ExperienceFactory(
            activity=activity,
            from_practitioner=True,
            fase='pioneer',
            tags=[tag1])
        ExperienceFactory(
            activity=activity,
            from_practitioner=False,
            fase='intermediate',
            tags=[tag1, tag2])
        ExperienceFactory(
            activity=activity,
            from_practitioner=True,
            fase='climax',
            tags=[tag2])

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert context["experiences_count"] == 3
        assert context["practitioner_count"] == 2
        assert context["passerby_count"] == 1
        assert context["chart_data_everyone"] == {'pioneer': 1, 'intermediate': 1, 'climax': 1}
        assert context["chart_data_practitioners"] == {'pioneer': 1, 'intermediate': 0, 'climax': 1}
        assert context["chart_data_passersby"] == {'pioneer': 0, 'intermediate': 1, 'climax': 0}

        tag_data_everyone = context["tag_data_everyone"]
        tag_counts = {tag['name']: tag['count'] for tag in tag_data_everyone}
        assert tag_counts == {"Tag1": 2, "Tag2": 2}
