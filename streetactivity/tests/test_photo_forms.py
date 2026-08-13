
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from streetactivity.forms import StreetActivityPhotoForm
from streetactivity.models import StreetActivityPhoto
from travelingguestbook.factories import StreetActivityFactory


class TestStreetActivityPhotoForm:
    '''Test the StreetActivityPhotoForm.s'''
    def create_image_content(self, size=(100, 100)):
        '''Create the image content that can be reused through the tests'''
        image = Image.new("RGB", size, color=(255, 0, 0))  # type: ignore[reportArgumentType]
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)
        return image_file.read()

    def test_form_valid_with_valid_image(self, temporary_media_root):
        """Test that the form is valid with a valid image file."""
        activity = StreetActivityFactory()
        image = SimpleUploadedFile(
            "test.jpg", self.create_image_content(), content_type="image/jpeg"
        )
        form_data = {'image': image}
        form = StreetActivityPhotoForm(data=form_data, files={'image': image})
        assert form.is_valid()
        photo = form.save(commit=False)
        photo.activity = activity
        photo.save()
        assert StreetActivityPhoto.objects.count() == 1

    def test_form_invalid_with_invalid_file_extension(self, temporary_media_root):
        """Test that the form raises a ValidationError for an invalid file extension."""
        image = SimpleUploadedFile(
            "test.pdf", self.create_image_content(), content_type="application/pdf"
        )
        form = StreetActivityPhotoForm(files={'image': image})
        assert not form.is_valid()
        assert 'image' in form.errors
        assert 'Alleen JPG, JPEG en PNG bestanden zijn toegestaan.' in str(form.errors['image'])

    def test_form_invalid_with_too_large_file(self, temporary_media_root):
        """Test that the form raises a ValidationError for a file that is too large."""
        large_image_content = self.enlarge_image(self.create_image_content((2000, 2000)))

        image = SimpleUploadedFile(
            "large_image.jpg", large_image_content, content_type="image/jpeg"
        )
        form = StreetActivityPhotoForm(files={'image': image})
        assert not form.is_valid()
        assert 'image' in form.errors
        assert 'Bestand is te groot.' in str(form.errors['image'])

    def enlarge_image(self, image_content):
        '''Create a big buffer by repeating the contents to the desired size
        Then cut at the exact sie'''
        target_size = 6 * 1024 * 1024  # 6MB
        large_image_content = image_content * (target_size // len(image_content) + 1)
        return large_image_content[:target_size]

    def test_form_invalid_without_image(self):
        """Test that the form is invalid if no image is provided."""
        form = StreetActivityPhotoForm(files={})
        assert not form.is_valid()
        assert 'image' in form.errors
        assert 'Dit veld is vereist.' in str(form.errors['image'])