from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from streetactivity.models import StreetActivity
from travelingguestbook.factories import UserFactory, WordFactory, StreetActivityFactory

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

    def test_streetactivity_updateview(self, auto_login_user):
        """Test the StreetActivity update view to ensure it returns a 200 status code
        and contains the expected form in context."""
        client, _ = auto_login_user()
        activity = StreetActivityFactory()
        update_url = reverse("update-streetactivity", args=[activity.id])

        updated_data = {
            "name": "Updated straatspel",
            "description": activity.description,
            "method": activity.method,
            "question": activity.question,
            "supplies": activity.supplies
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        activity.refresh_from_db()
        assert activity.name == "Updated straatspel"

    def test_streetactivity_update_by_anonymous(self, client):
        """Given an anonymous user tries to update a streetactivity,
        test if that is not allowed"""

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
        # Maak test straatspelen aan met factory
        StreetActivityFactory(name="Test straatspel 1")
        StreetActivityFactory(name="Test straatspel 2")

        response = client.get(reverse("streetactivity-list"))
        content = response.content.decode()

        assert "Test straatspel 1" in content
        assert "Test straatspel 2" in content

    def test_list_view_pagination(self, client):
        """Test that pagination works correctly"""
        for i in range(15):
            StreetActivityFactory(name=f"Pagination Test {i}")

        response = client.get(reverse("streetactivity-list"))

        assert response.context["is_paginated"]
        assert len(response.context["activities"]) == 10

    def test_list_view_ordering(self, client):
        """Test that activities are ordered by name"""
        StreetActivityFactory(name="Zebra straatspel")
        StreetActivityFactory(name="Alpha straatspel")
        StreetActivityFactory(name="Beta straatspel")

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
            name="Detail Test straatspel",
            description="Dit is een test beschrijving."
        )

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))

        assert "Detail Test straatspel" in response.text
        assert "Dit is een test beschrijving" in response.text

    def test_detail_view_context_data(self, client):
        """Test that the correct context data is provided in the detail view"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert "activity" in context
        assert context["activity"] == activity

    def test_detail_view_word_statistics(self, client):
        """Test that word statistics are correctly calculated and included in context"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert "words_count" in context

    def test_detail_view_no_words(self, client):
        """Test that the detail view handles activities with no words gracefully"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context

        assert context["words_count"] == 0

    def test_negative_words_remaining(self, client):
        """Test if that when there are no words,
        then the words_remaining results in 0 and not -3"""
        activity = StreetActivityFactory()
        response = client.get(reverse("streetactivity-detail", args=[activity.id]))
        context = response.context
        assert context['words_remaining'] == 0

class TestStreetActivityDetailViewContextWordTree:
    """Test the context data for the WordTree of StreetActivityDetailView."""

    def test_activity_view_contains_activity_stats(self, client):
        """Test that activity view has activity-specific stats."""
        activity = StreetActivityFactory(name="Test Game")
        user = UserFactory()

        WordFactory.create_batch(5, user=user, activity=activity)

        url = reverse('streetactivity-detail', args=[activity.id])
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['activity'] == activity

        # Check activity stats
        assert 'total_words' in response.context
        assert response.context['total_words'] == 5
        assert 'unique_words' in response.context
        assert 'recent_words' in response.context

    def test_activity_view_wordtree_base_filter(self, client):
        """Test that wordtree base filter is the activity."""
        activity = StreetActivityFactory(name="Test Game")

        url = reverse('streetactivity-detail', args=[activity.id])
        response = client.get(url)

        base_filter = response.context['wordtree_data']['base_filter']
        assert base_filter['type'] == 'activity'
        assert base_filter['value'] == activity.id
        assert base_filter['display_name'] == activity.name

    def test_activity_view_with_date_filter(self, client):
        """Test applying date filter to activity view."""
        activity = StreetActivityFactory()
        user = UserFactory()

        # Words from different dates
        WordFactory(
            user=user,
            activity=activity,
            word="today",
            date_created=timezone.now()
        )

        WordFactory(
            user=user,
            activity=activity,
            word="old",
            date_created=timezone.now() - timedelta(days=10)
        )

        # Test with 'today' filter
        url = reverse('streetactivity-detail', args=[activity.id])
        response = client.get(url, {'date_filter': 'today'})

        wordtree_data = response.context['wordtree_data']
        assert wordtree_data['total_count'] == 1
        assert wordtree_data['words'][0]['word'] == 'today'
        assert wordtree_data['current_filters']['date'] == 'today'

        # Test with 'all' filter
        response = client.get(url, {'date_filter': 'all'})
        wordtree_data = response.context['wordtree_data']
        assert wordtree_data['total_count'] == 2

    def test_activity_view_no_activity_filter_option(self, client):
        """Test that activity view doesn't show activity filter."""
        activity = StreetActivityFactory()

        url = reverse('streetactivity-detail', args=[activity.id])
        response = client.get(url)

        # Activity view should not have activity filter options
        assert 'activity_filter_options' not in response.context
        assert 'current_activity_filter' not in response.context

    def test_activity_view_date_filter_options(self, client):
        """Test that activity view has correct date filter options."""
        activity = StreetActivityFactory()

        url = reverse('streetactivity-detail', args=[activity.id])
        response = client.get(url)

        date_options = response.context['date_filter_options']
        assert len(date_options) == 4
        assert date_options[0]['value'] == 'all'
        assert date_options[1]['value'] == 'today'
        assert date_options[2]['value'] == 'week'
        assert date_options[3]['value'] == 'month'
