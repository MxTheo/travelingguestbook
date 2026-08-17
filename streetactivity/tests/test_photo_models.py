import pytest
from django.core.exceptions import ValidationError

from streetactivity.models import StreetActivityPhoto
from travelingguestbook.factories import (
    StreetActivityFactory,
    StreetActivityPhotoFactory,
)


class TestStreetActivityPhotoModel:
    '''Test the StreetActivityPhoto model.'''
    def test_model_exists(self):
        """Test that the StreetActivityPhoto model exists."""
        assert StreetActivityPhoto.objects.count() == 0

    def test_foreign_key_to_activity(self, temporary_media_root):
        """Test that StreetActivityPhoto has a ForeignKey to StreetActivity (renamed to activity)."""
        activity = StreetActivityFactory()
        photo = StreetActivityPhotoFactory(activity=activity)
        assert photo.activity == activity
        assert StreetActivityPhoto.objects.get(pk=photo.pk).activity == activity

    def test_image_field_exists(self, temporary_media_root):
        """Test that StreetActivityPhoto has an ImageField."""
        photo = StreetActivityPhotoFactory()
        assert photo.image is not None

    def test_uploaded_at_field_exists(self, temporary_media_root):
        """Test that StreetActivityPhoto has an uploaded_at field."""
        photo = StreetActivityPhotoFactory()
        assert photo.uploaded_at is not None

    def test_string(self, temporary_media_root):
        """Test that StreetActivityPhoto returns the correct string of
        Photo for {self.activity} (uploaded at {self.uploaded_at})"""
        photo = StreetActivityPhotoFactory()
        expected_string = f"{photo.activity} - {photo.uploaded_at}"
        assert str(photo) == expected_string


class TestStreetActivityPhotoModelValidation:
    '''Test the validation of the StreetActivityPhoto model.'''
    def test_image_field_validation_valid_file(self, temporary_media_root):
        """Test that a valid image file (JPG/JPEG/PNG) is accepted."""
        activity = StreetActivityFactory()
        photo = StreetActivityPhotoFactory(activity=activity)
        assert photo.image.name.endswith(('.jpg', '.jpeg', '.png'))

    def test_image_field_validation_invalid_file(self, temporary_media_root):
        """Test that an invalid file (e.g., PDF) raises a ValidationError."""
        activity = StreetActivityFactory()
        invalid_photo = StreetActivityPhoto(
            activity=activity,
            image='test.pdf'
        )
        with pytest.raises(ValidationError):
            invalid_photo.full_clean()

    def test_image_field_is_required_when_saving(self, temporary_media_root):
        """
        Test that the image field is required when saving a StreetActivityPhoto.
        Django's ImageField raises a ValidationError if the image is missing.
        """
        activity = StreetActivityFactory()
        photo = StreetActivityPhoto(activity=activity)  # Create without image
        with pytest.raises(ValidationError):
            photo.full_clean()

    
