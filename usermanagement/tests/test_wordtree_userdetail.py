from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from travelingguestbook.factories import StreetActivityFactory, WordFactory, UserFactory

class TestUserDetailViewContext:
    """Test the context data of UserDetailView."""

    def test_user_view_contains_user_stats(self, client):
        """Test that user view has user-specific stats."""
        user = UserFactory(username="testuser", first_name="Test", last_name="User")
        activity1 = StreetActivityFactory()
        activity2 = StreetActivityFactory()

        WordFactory.create_batch(3, user=user, activity=activity1, word="courage")
        WordFactory.create_batch(2, user=user, activity=activity2, word="kindness")

        url = reverse('user', args=[user.username])
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['profile_user'] == user

        assert 'total_words' in response.context
        assert response.context['total_words'] == 5
        assert 'unique_words' in response.context
        assert response.context['unique_words'] == 2
        assert 'top_words' in response.context

        top_words = response.context['top_words']
        assert len(top_words) == 2
        assert top_words[0]['word'] == 'courage'
        assert top_words[0]['count'] == 3

    def test_user_view_wordtree_base_filter(self, client):
        """Test that wordtree base filter is the user."""
        user = UserFactory(username="testuser")

        url = reverse('user', args=[user.username])
        response = client.get(url)

        base_filter = response.context['wordtree_data']['base_filter']
        assert base_filter['type'] == 'user'
        assert base_filter['value'] == user.username
        assert base_filter['display_name'] == user.username

    def test_user_view_with_date_filter(self, client):
        """Test applying date filter to user view."""
        user = UserFactory()
        activity = StreetActivityFactory()

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

        url = reverse('user', args=[user.username])
        response = client.get(url, {'date_filter': 'today'})

        wordtree_data = response.context['wordtree_data']
        assert wordtree_data['total_count'] == 1
        assert wordtree_data['current_filters']['date'] == 'today'

    def test_user_view_with_activity_filter(self, client):
        """Test applying activity filter to user view."""
        user = UserFactory()
        activity1 = StreetActivityFactory(name="Game 1")
        activity2 = StreetActivityFactory(name="Game 2")

        WordFactory(user=user, activity=activity1, word="courage")
        WordFactory(user=user, activity=activity1, word="courage")
        WordFactory(user=user, activity=activity2, word="kindness")

        url = reverse('user', args=[user.username])
        response = client.get(url, {'activity_filter': activity1.id})

        wordtree_data = response.context['wordtree_data']
        assert wordtree_data['total_count'] == 2
        assert wordtree_data['current_filters']['activity'] == str(activity1.id)

        # Should only have words from activity1
        words = [w['word'] for w in wordtree_data['words']]
        assert 'courage' in words
        assert 'kindness' not in words

    def test_user_view_activity_filter_options(self, client):
        """Test that user view has correct activity filter options."""
        user = UserFactory()
        activity1 = StreetActivityFactory(name="Game 1")
        activity2 = StreetActivityFactory(name="Game 2")
        activity3 = StreetActivityFactory(name="Game 3")

        WordFactory(user=user, activity=activity1)
        WordFactory(user=user, activity=activity2)

        url = reverse('user', args=[user.username])
        response = client.get(url)

        activity_options = response.context['activity_filter_options']

        # Should include 'all' + the two activities user has words in
        assert len(activity_options) == 3
        assert activity_options[0]['value'] == 'all'

        # Find the activities in options
        option_values = [opt['value'] for opt in activity_options]
        assert activity1.id in option_values
        assert activity2.id in option_values
        assert activity3.id not in option_values

    def test_user_view_combined_filters(self, client):
        """Test combining date and activity filters."""
        user = UserFactory()
        activity = StreetActivityFactory()

        WordFactory(
            user=user,
            activity=activity,
            word="recent",
            date_created=timezone.now()
        )
        WordFactory(
            user=user,
            activity=activity,
            word="old",
            date_created=timezone.now() - timedelta(days=10)
        )

        url = reverse('user', args=[user.username])
        response = client.get(url, {
            'date_filter': 'today',
            'activity_filter': activity.id
        })

        wordtree_data = response.context['wordtree_data']
        assert wordtree_data['total_count'] == 1
        assert wordtree_data['words'][0]['word'] == 'recent'

        assert wordtree_data['current_filters']['date'] == 'today'
        assert wordtree_data['current_filters']['activity'] == str(activity.id)
