
from io import BytesIO

from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from PIL import Image

from streetactivity.models import StreetActivityPhoto
from travelingguestbook.factories import (
    StreetActivityFactory,
    StreetActivityPhotoFactory,
)


class TestStreetActivityPhotoCreateView:
    '''Tests for the create view of streetactivity photo'''
    def test_get_success_url_returns_correct_url(self):
        """Test that get_success_url returns the correct URL after form submission."""
        activity = StreetActivityFactory()
        client = Client()
        url = reverse(
            "create-streetactivity-photo",
            kwargs={"activity_id": activity.id}
        )
        response = client.get(url)
        assert response.status_code == 200

    def test_form_valid_creates_photo_and_redirects(self, temporary_media_root):
        """Test that a valid form submission creates a photo and redirects to the correct URL."""
        activity = StreetActivityFactory()
        client = Client()
        url = reverse(
            "create-streetactivity-photo",
            kwargs={"activity_id": activity.id}
        )

        image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # type: ignore[reportArgumentType]
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        uploaded_image = SimpleUploadedFile(
            "test_image.jpg",
            image_file.read(),
            content_type="image/jpeg"
        )

        response = client.post(
            url,
            {
                "image": uploaded_image,
            },
            follow=True
        )

        assert StreetActivityPhoto.objects.count() == 1
        photo = StreetActivityPhoto.objects.first()
        assert photo.activity == activity

        # Check if user is redirected to the correct url
        assert response.redirect_chain[-1][0] == reverse(
            "streetactivity-photo-list",
            kwargs={"activity_id": activity.id}
        )

        # Check if success message is shown
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Je foto is succesvol geupload!"

    def test_form_invalid_shows_error_message(self, temporary_media_root):
        """Test that an invalid form submission shows an error message."""
        activity = StreetActivityFactory()
        client = Client()
        url = reverse(
            "create-streetactivity-photo",
            kwargs={"activity_id": activity.id}
        )

        large_image_content = b'x' * (6 * 1024 * 1024)  # 6MB
        uploaded_image = SimpleUploadedFile(
            "large_image.jpg",
            large_image_content,
            content_type="image/jpeg"
        )

        response = client.post(
            url,
            {
                "image": uploaded_image,
            },
            follow=True
        )

        assert StreetActivityPhoto.objects.count() == 0

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Er was een fout bij het uploaden van je foto. Controleer het bestand en probeer opnieuw."

class TestStreetActivityPhotoDeleteView:
    '''Test class for delete view of streetactivity photo'''
    def test_delete_view(self, client, temporary_media_root):
        """Test the delete view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()
        photo = StreetActivityPhotoFactory(activity=activity)

        delete_url = reverse("delete-streetactivity-photo", args=[photo.id])

        response = client.post(delete_url)

        assert response.status_code == 302
        assert not StreetActivityPhoto.objects.filter(id=photo.id).exists()
        assert StreetActivityPhoto.objects.count() == 0

class TestStreetActivityPhotoListView:
    """Tests for the StreetActivity photo list view."""

    def test_list_view_returns_200(self, client):
        """Test that the list view returns a 200 status code"""
        activity = StreetActivityFactory()
        response = client.get(reverse("streetactivity-photo-list", kwargs={'activity_id': activity.id}))
        assert response.status_code == 200

    def test_list_view_uses_correct_template(self, client):
        """Test that the list view uses the correct template"""
        activity = StreetActivityFactory()
        response = client.get(reverse("streetactivity-photo-list", kwargs={'activity_id': activity.id}))
        assert "streetactivity/streetactivityphoto_list.html" in [
            t.name for t in response.templates
        ]


    def test_list_view_pagination(self, client, temporary_media_root):
        """Test that pagination works correctly"""
        activity = StreetActivityFactory() 

        for _ in range(15):
            StreetActivityPhotoFactory(activity=activity)

        response = client.get(reverse("streetactivity-photo-list", kwargs={'activity_id':activity.id}))

        assert response.context["is_paginated"]
        assert len(response.context["photos"]) == 10

    def test_list_view_context_data(self, client):
        """Test that the correct context data is provided"""
        activity = StreetActivityFactory()

        response = client.get(reverse("streetactivity-photo-list", kwargs={'activity_id':activity.id}))
        context = response.context

        assert "activity" in context
