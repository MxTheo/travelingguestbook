# core/tests/test_mixins.py
from datetime import timedelta
import pytest
from django.utils import timezone

from core.utils.mixins import WordTreeMixin, ActivityFilterMixin
from travelingguestbook.factories import UserFactory, StreetActivityFactory, WordFactory
from streetactivity.models import Word


class TestWordTreeMixin:
    """Test suite for WordTreeMixin."""

    @pytest.fixture
    def mixin(self):
        """Create a mixin instance for testing."""
        class TestView(WordTreeMixin):
            def get_base_queryset(self):
                return Word.objects.all()

            def get_wordtree_base_filter(self):
                return {'type': 'test', 'value': 'test123', 'display_name': 'Test Filter'}

        return TestView()

    @pytest.fixture
    def setup_words(self, db):
        """Create test words with different dates and activities."""
        user = UserFactory()
        activity1 = StreetActivityFactory(name="Game 1")
        activity2 = StreetActivityFactory(name="Game 2")

        # Words from different time periods
        words = {
            'today': WordFactory(
                user=user,
                activity=activity1,
                word="courage",
                date_created=timezone.now()
            ),
            'yesterday': WordFactory(
                user=user,
                activity=activity1,
                word="kindness",
                date_created=timezone.now() - timedelta(days=1)
            ),
            'last_week': WordFactory(
                user=user,
                activity=activity1,
                word="patience",
                date_created=timezone.now() - timedelta(days=8)
            ),
            'last_month': WordFactory(
                user=user,
                activity=activity2,
                word="wisdom",
                date_created=timezone.now() - timedelta(days=35)
            ),
            'old': WordFactory(
                user=user,
                activity=activity2,
                word="strength",
                date_created=timezone.now() - timedelta(days=100)
            ),
        }

        # Add duplicate words to test frequency counting
        WordFactory(
            user=user,
            activity=activity1,
            word="courage",  # Another courage
            date_created=timezone.now()
        )

        return {
            'user': user,
            'activity1': activity1,
            'activity2': activity2,
            'words': words
        }

    def test_get_wordtree_base_filter_default(self):
        """Test default base filter returns correct structure."""
        class TestView(WordTreeMixin):
            pass

        mixin = TestView()
        result = mixin.get_wordtree_base_filter()

        assert result == {
            'type': 'all',
            'value': '',
            'display_name': 'All words'
        }

    def test_get_wordtree_base_filter_overridden(self, mixin):
        """Test overridden base filter returns custom values."""
        result = mixin.get_wordtree_base_filter()

        assert result == {
            'type': 'test',
            'value': 'test123',
            'display_name': 'Test Filter'
        }

    def test_get_base_queryset_default(self):
        """Test default base queryset returns all words."""
        class TestView(WordTreeMixin):
            pass

        # Create some words
        WordFactory.create_batch(3)

        mixin = TestView()
        result = mixin.get_base_queryset()

        assert result.count() == 3
        assert isinstance(result, type(Word.objects.all()))

    def test_apply_date_filter_today(self, mixin, setup_words):
        """Test date filter for 'today' returns only today's words."""
        queryset = Word.objects.all()
        result = mixin.apply_date_filter(queryset, 'today')

        # Should only include today's words (courage appears twice)
        assert result.count() == 2
        assert all(w.word == "courage" for w in result)

    def test_apply_date_filter_week(self, mixin, setup_words):
        """Test date filter for 'week' returns words from last 7 days."""
        queryset = Word.objects.all()
        result = mixin.apply_date_filter(queryset, 'week')

        # Should include today and yesterday (courage x2, kindness)
        assert result.count() == 3
        words = set(result.values_list('word', flat=True))
        assert words == {"courage", "kindness"}

    def test_apply_date_filter_month(self, mixin, setup_words):
        """Test date filter for 'month' returns words from last 30 days."""
        queryset = Word.objects.all()
        result = mixin.apply_date_filter(queryset, 'month')

        # Should include today, yesterday, last week (courage x2, kindness, patience)
        assert result.count() == 4
        words = set(result.values_list('word', flat=True))
        assert words == {"courage", "kindness", "patience"}

    def test_apply_date_filter_all(self, mixin, setup_words):
        """Test date filter for 'all' returns all words."""
        queryset = Word.objects.all()
        result = mixin.apply_date_filter(queryset, 'all')

        assert result.count() == 6  # All 5 words + duplicate courage

    def test_apply_date_filter_invalid(self, mixin, setup_words):
        """Test invalid date filter returns original queryset."""
        queryset = Word.objects.all()
        original_count = queryset.count()

        result = mixin.apply_date_filter(queryset, 'invalid_filter')

        assert result.count() == original_count

    def test_apply_activity_filter_specific(self, mixin, setup_words):
        """Test activity filter for specific activity ID."""
        queryset = Word.objects.all()
        result = mixin.apply_activity_filter(queryset, setup_words['activity1'].id)

        # Activity1 has: courage x2, kindness, patience
        assert result.count() == 4
        assert all(w.activity_id == setup_words['activity1'].id for w in result)

    def test_apply_activity_filter_all(self, mixin, setup_words):
        """Test activity filter with 'all' returns all words."""
        queryset = Word.objects.all()
        result = mixin.apply_activity_filter(queryset, 'all')

        assert result.count() == 6

    def test_apply_activity_filter_invalid_id(self, mixin, setup_words):
        """Test invalid activity ID returns original queryset."""
        queryset = Word.objects.all()
        original_count = queryset.count()

        result = mixin.apply_activity_filter(queryset, 99999)

        assert result.count() == original_count

    def test_apply_activity_filter_non_integer(self, mixin, setup_words):
        """Test non-integer activity filter returns original queryset."""
        queryset = Word.objects.all()
        original_count = queryset.count()

        result = mixin.apply_activity_filter(queryset, 'not-an-integer')

        assert result.count() == original_count

    def test_get_word_frequencies(self, mixin, setup_words):
        """Test word frequency calculation."""
        queryset = Word.objects.all()
        result = mixin.get_word_frequencies(queryset, limit=10)

        # Should count frequencies: courage=2, others=1
        frequencies = {item['word']: item['weight'] for item in result}

        assert frequencies['courage'] == 2
        assert frequencies['kindness'] == 1
        assert frequencies['patience'] == 1
        assert frequencies['wisdom'] == 1
        assert frequencies['strength'] == 1
        assert len(result) == 5  # 5 unique words

    def test_get_word_frequencies_with_limit(self, mixin, setup_words):
        """Test word frequency calculation with limit."""
        queryset = Word.objects.all()
        result = mixin.get_word_frequencies(queryset, limit=2)

        assert len(result) == 2
        # First two should be courage (weight=2) and any other (weight=1)
        assert result[0]['word'] == 'courage'
        assert result[0]['weight'] == 2
        assert result[1]['weight'] == 1

    def test_get_word_frequencies_empty_queryset(self, mixin):
        """Test word frequency calculation with empty queryset."""
        queryset = Word.objects.none()
        result = mixin.get_word_frequencies(queryset)

        assert result == []

    def test_get_date_filter_options(self, mixin):
        """Test date filter options return correct structure."""
        result = mixin.get_date_filter_options()

        assert len(result) == 4
        assert result[0] == {'value': 'all', 'label': 'All time'}
        assert result[1] == {'value': 'today', 'label': 'Today'}
        assert result[2] == {'value': 'week', 'label': 'Past week'}
        assert result[3] == {'value': 'month', 'label': 'Past month'}

    def test_get_wordtree_context_no_filters(self, mixin, setup_words):
        """Test wordtree context with no filters applied."""
        base_queryset = Word.objects.all()
        current_filters = {'date': 'all', 'activity': 'all'}

        result = mixin.get_wordtree_context(base_queryset, current_filters)

        assert 'wordtree_data' in result
        assert 'date_filter_options' in result
        assert 'current_date_filter' in result

        wordtree_data = result['wordtree_data']
        assert wordtree_data['total_count'] == 6
        assert len(wordtree_data['words']) == 5
        assert wordtree_data['base_filter'] == {'type': 'test', 'value': 'test123', 'display_name': 'Test Filter'}
        assert wordtree_data['current_filters'] == current_filters

    def test_get_wordtree_context_with_date_filter(self, mixin, setup_words):
        """Test wordtree context with date filter applied."""
        base_queryset = Word.objects.all()
        current_filters = {'date': 'today', 'activity': 'all'}

        result = mixin.get_wordtree_context(base_queryset, current_filters)

        wordtree_data = result['wordtree_data']
        assert wordtree_data['total_count'] == 2  # Two courage words today
        assert result['current_date_filter'] == 'today'

    def test_get_wordtree_context_with_activity_filter(self, mixin, setup_words):
        """Test wordtree context with activity filter applied."""
        base_queryset = Word.objects.all()
        current_filters = {'date': 'all', 'activity': setup_words['activity2'].id}

        result = mixin.get_wordtree_context(base_queryset, current_filters)

        wordtree_data = result['wordtree_data']
        # Activity2 has: wisdom, strength
        assert wordtree_data['total_count'] == 2
        words = [w['word'] for w in wordtree_data['words']]
        assert set(words) == {'wisdom', 'strength'}


class TestActivityFilterMixin:
    """Test suite for ActivityFilterMixin."""

    @pytest.fixture
    def mixin(self):
        """Create an ActivityFilterMixin instance for testing."""
        class TestView(ActivityFilterMixin):
            def get_base_queryset(self):
                return Word.objects.all()

            def get_wordtree_base_filter(self):
                return {'type': 'test', 'value': 'test123'}

        return TestView()

    @pytest.fixture
    def setup_words(self, db):
        """Create test words across multiple activities."""
        user = UserFactory()
        activity1 = StreetActivityFactory(name="Game Alpha")
        activity2 = StreetActivityFactory(name="Game Beta")
        activity3 = StreetActivityFactory(name="Game Gamma")  # No words

        # Words in activity1
        WordFactory.create_batch(2, user=user, activity=activity1, word="courage")
        WordFactory(user=user, activity=activity1, word="kindness")

        # Words in activity2
        WordFactory(user=user, activity=activity2, word="wisdom")
        WordFactory(user=user, activity=activity2, word="patience")

        return {
            'user': user,
            'activity1': activity1,
            'activity2': activity2,
            'activity3': activity3,
        }

    def test_get_activity_filter_options(self, mixin, setup_words):
        """Test activity filter options generation."""
        base_queryset = Word.objects.all()
        result = mixin.get_activity_filter_options(base_queryset)

        # Should include 'all' + activities that have words (activity1, activity2)
        assert len(result) == 3
        assert result[0] == {'value': 'all', 'label': 'All activities'}

        # Find the activities in options
        options_dict = {opt['value']: opt['label'] for opt in result}
        assert setup_words['activity1'].id in options_dict
        assert options_dict[setup_words['activity1'].id] == 'Game Alpha'
        assert setup_words['activity2'].id in options_dict
        assert options_dict[setup_words['activity2'].id] == 'Game Beta'
        assert setup_words['activity3'].id not in options_dict  # No words

    def test_get_activity_filter_options_empty_queryset(self, mixin):
        """Test activity filter options with empty queryset."""
        base_queryset = Word.objects.none()
        result = mixin.get_activity_filter_options(base_queryset)

        # Should only have 'all' option
        assert len(result) == 1
        assert result[0] == {'value': 'all', 'label': 'All activities'}

    def test_get_wordtree_context_with_activity_filter_options(self, mixin, setup_words):
        """Test wordtree context includes activity filter options."""
        base_queryset = Word.objects.all()
        current_filters = {'date': 'all', 'activity': 'all'}

        result = mixin.get_wordtree_context(base_queryset, current_filters)

        # Should have activity filter options
        assert 'activity_filter_options' in result
        assert 'current_activity_filter' in result

        activity_options = result['activity_filter_options']
        assert len(activity_options) == 3  # 'all' + 2 activities
        assert result['current_activity_filter'] == 'all'

    def test_get_wordtree_context_with_active_activity_filter(self, mixin, setup_words):
        """Test wordtree context with active activity filter."""
        base_queryset = Word.objects.all()
        current_filters = {'date': 'all', 'activity': setup_words['activity1'].id}

        result = mixin.get_wordtree_context(base_queryset, current_filters)

        assert result['current_activity_filter'] == setup_words['activity1'].id

        # Should only show words from activity1
        wordtree_data = result['wordtree_data']
        assert wordtree_data['total_count'] == 3  # 2 courage + 1 kindness