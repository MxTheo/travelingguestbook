from django.urls import reverse

from travelingguestbook.factories import (
    StreetActivityFactory,
    StreetActivityPhotoFactory,
)


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

    def test_get_random_photos_returns_correct_number_of_photos(self, client):
        """Test that home shows 4 random photos when there are more than 4 photos in the database"""
        for _ in range(5):
            StreetActivityPhotoFactory()
        response = client.get(reverse('home'))
        assert len(response.context['photos']) == 4
