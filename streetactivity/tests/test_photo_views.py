from django.urls import reverse

from travelingguestbook.factories import ReflectionFactory


class TestReflectionPhotoListView:
    """Tests for the StreetActivity photo list view."""

    def test_list_view_returns_200(self, client):
        """Test that the list view returns a 200 status code"""
        response = client.get(reverse("reflectionphoto-list"))
        assert response.status_code == 200

    def test_list_view_uses_correct_template(self, client):
        """Test that the list view uses the correct template"""
        response = client.get(reverse("reflectionphoto-list"))
        assert "streetactivity/reflectionphoto_list.html" in [
            t.name for t in response.templates
        ]


    def test_list_view_pagination(self, client):
        """Test that pagination works correctly"""
        for _ in range(15):
            ReflectionFactory()

        response = client.get(reverse("reflectionphoto-list"))

        assert response.context["is_paginated"]
        assert len(response.context["reflections_with_photo"]) == 10
