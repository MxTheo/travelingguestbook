from django.urls import reverse
import pytest
from datetime import timedelta
from django.utils import timezone
from travelingguestbook.factories import UserFactory, StreetActivityFactory, WordFactory


class TestHome:
    """Tests for the HomeView"""
    def test_returns_200(self, client):
        """Test if the home page is reached"""
        response = client.get(reverse('home'))
        assert response.status_code == 200

    def test_if_activities_remaining_does_not_return_negative(self, client):
        """Test that when there are 0 activities, the remaining activities is not set to -4"""
        response = client.get(reverse('home'))
        assert response.context["activities_remaining"] == 0

    def test_if_featured_activities_are_there(self,client):
        """Test that when there are 6 activities, that there are 4 activities on the homepage"""
        for i in range(7):
            StreetActivityFactory(name=f"spel{i}")
        response = client.get(reverse('home'))
        assert len(response.context['featured_activities']) == 4



class TestHomeViewContextWordTree:
    """Test the context data of the WordTree of HomeView."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, db):
        """Set up test data."""
        self.user = UserFactory()
        self.activity = StreetActivityFactory(name="Test Game")
        
        # Create words with different dates
        # Today
        WordFactory(
            activity=self.activity,
            word="courage",
            date_created=timezone.now()
        )
        WordFactory(
            activity=self.activity,
            word="courage",  # Duplicate
            date_created=timezone.now()
        )
        
        # Yesterday (within week)
        WordFactory(
            activity=self.activity,
            word="kindness",
            date_created=timezone.now() - timedelta(days=1)
        )
        
        # 5 days ago (within week)
        WordFactory(
            activity=self.activity,
            word="patience",
            date_created=timezone.now() - timedelta(days=5)
        )
        
        # 10 days ago (outside week)
        WordFactory(
            activity=self.activity,
            word="wisdom",
            date_created=timezone.now() - timedelta(days=10)
        )
    
    def test_home_view_contains_wordtree_context(self, client):
        """Test home view has wordtree data in context."""
        url = reverse('home')
        response = client.get(url)
        
        assert 'wordtree_data' in response.context
        assert 'date_filter_options' in response.context
        assert 'wordtree_container_id' in response.context
        
        wordtree_data = response.context['wordtree_data']
        assert 'words' in wordtree_data
        assert 'total_count' in wordtree_data
        assert 'base_filter' in wordtree_data
        assert 'current_filters' in wordtree_data
    
    def test_home_view_default_week_filter(self, client):
        """Test home view defaults to week filter (only last 7 days)."""
        url = reverse('home')
        response = client.get(url)
        
        wordtree_data = response.context['wordtree_data']
        
        # Should include: courage x2, kindness, patience (4 words)
        # Exclude: wisdom (from 10 days ago)
        assert wordtree_data['total_count'] == 4
        
        # Check frequencies
        words = {item['word']: item['weight'] for item in wordtree_data['words']}
        assert words['courage'] == 2
        assert words['kindness'] == 1
        assert words['patience'] == 1
        assert 'wisdom' not in words
        
        # Check current filters
        assert wordtree_data['current_filters']['date'] == 'week'
    
    def test_home_view_base_filter_correct(self, client):
        """Test that base filter indicates 'week' type."""
        url = reverse('home')
        response = client.get(url)
        
        base_filter = response.context['wordtree_data']['base_filter']
        assert base_filter['type'] == 'week'
        assert 'display_name' in base_filter
        assert 'value' in base_filter
    
    def test_home_view_container_id(self, client):
        """Test home view has correct container ID."""
        url = reverse('home')
        response = client.get(url)
        
        assert response.context['wordtree_container_id'] == 'global'