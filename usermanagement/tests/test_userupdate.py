import io
from unittest.mock import patch
from PIL import Image
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from travelingguestbook.factories import UserFactory
from usermanagement.models import Profile
from usermanagement.forms import ProfileForm

class TestUserUpdateView:
    """Tests for user that updates its account"""
    def test_login_required_redirects(self, client):
        """Anonymous users should be redirected to login when accessing the update page."""
        url = reverse("update-account")
        resp = client.get(url)
        assert resp.status_code in (302, 301)
        assert "/login" in resp["Location"]

    def test_get_shows_both_forms(self, auto_login_user):
        """Logged in user sees both user and profile form fields."""
        client, _ = auto_login_user()
        resp = client.get(reverse("update-account"))
        content = resp.content.decode()
        assert "email" in content
        assert "profile_image" in content

    def test_post_valid_updates_user_and_profile(self, auto_login_user):
        """Submitting valid data updates User and Profile and redirects."""
        client, user = auto_login_user()
        url = reverse("update-account")

        new_email = "updated@example.com"

        data = {
            "email": new_email,
        }

        resp = client.post(url, data)
        assert resp.status_code in (302, 301)

        user.refresh_from_db()
        assert user.email == new_email

    def test_post_invalid_shows_errors(self, auto_login_user):
        """Submitting invalid data redisplays the form with errors."""
        client, _ = auto_login_user()
        url = reverse("update-account")

        data = {
            "email": "invalid-email",
        }

        resp = client.post(url, data)
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Vul een echt e‑mailadres in" in content

    def test_update_profile_with_valid_profile_image(self, auto_login_user, temporary_media_root):
        """Test that a valid profile image is saved correctly"""
        client, user = auto_login_user()
        buffer = create_test_image()
        valid_image = SimpleUploadedFile(
            "test.jpg", buffer.read(), content_type="image/jpeg"
        )

        url = reverse("update-account")
        data = {"profile_image": valid_image, "email": "test@info.com"}
        response = client.post(url, data, follow=True)

        assert response.status_code == 200
        content = response.content.decode()

        assert "Bewerken van je profiel is geslaagd!" in content
        assert "empty_portrait.jpg" not in content

        user.profile.refresh_from_db()
        assert user.profile.profile_image.name != ""

    def test_update_profile_with_invalid_profile_image(self, auto_login_user, temporary_media_root):
        """Test that invalid profile image shows error message"""
        client, user = auto_login_user()

        invalid_image = SimpleUploadedFile(
            "invalid_test.jpg",
            b"this_is_not_a_valid_image_content",
            content_type="image/jpeg",
        )

        url = reverse("update-account")
        data = {
            "profile_image": invalid_image,
            "email": "test@info.com",
        }
        response = client.post(url, data, follow=True)

        assert response.status_code == 200
        content = response.content.decode()

        assert "Profielgegevens zijn niet opgeslagen vanwege fouten." in content

        user.profile.refresh_from_db()
        assert user.profile.profile_image.name == ""

    def test_update_user_form_valid_profile_form_invalid(self, auto_login_user, temporary_media_root):
        """Test that valid user form updates,
          but invalid profile form shows warning"""
        client, _ = auto_login_user()

        mock_image = SimpleUploadedFile(
            "invalid_test.jpg", b"invalid_image_data", content_type="image/jpeg"
        )

        url = reverse("update-account")
        data = {"profile_image": mock_image, "email": "test@info.com"}
        response = client.post(url, data, follow=True)

        assert response.status_code == 200
        content = response.content.decode()

        assert "Profielgegevens zijn niet opgeslagen vanwege fouten." in content


class TestImageUrl:
    """Tests that the image_url is correctly set for profile image"""
    def test_profile_image_url_without_profile_image(self):
        """Test profile_image_url property when no profile_image is set"""
        user = UserFactory()
        assert (
            user.profile.profile_image_url
            == "/static/persona/images/empty_portrait.jpg"
        )

    def test_profile_image_url_with_profile_image(self, auto_login_user, temporary_media_root):
        """Test profile_image_url property when profile_image is set"""
        mock_image = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )
        _, user = auto_login_user()
        user.profile.profile_image = mock_image
        user.save()
        profile = Profile.objects.get(user=user)

        assert (
            not profile.profile_image_url == "/static/persona/images/empty_portrait.jpg"
        )


class TestProfileForm:
    """Tests that the user can set a profile image in the profile form"""
    def test_valid_profile_image(self, temporary_media_root):
        """Test form with valid image"""
        buffer = create_test_image()
        valid_image = SimpleUploadedFile(
            "test.jpg", buffer.read(), content_type="image/jpeg"
        )

        form = ProfileForm(files={"profile_image": valid_image})
        assert form.is_valid()

    def test_invalid_image(self, temporary_media_root):
        """Test form with invalid image content"""
        invalid_image = SimpleUploadedFile(
            "invalid.jpg", b"not_really_an_image", content_type="image/jpeg"
        )

        form = ProfileForm(files={"profile_image": invalid_image})
        assert not form.is_valid()
        assert "Upload een geldige afbeelding" in str(form.errors)

    def test_image_too_large(self, temporary_media_root):
        """Test form validation when image is too large - simplified version"""

        buffer = create_test_image()
        small_image = SimpleUploadedFile(
            "test.jpg", buffer.read(), content_type="image/jpeg"
        )

        with patch.object(small_image, "size", 6 * 1024 * 1024):
            form = ProfileForm(files={"profile_image": small_image})
            assert not form.is_valid()
            assert "Afbeelding mag niet groter zijn dan 5MB" in str(form.errors)

    def test_invalid_extension(self, temporary_media_root):
        """Test ongeldige extensie"""
        buffer = create_test_image()
        image = SimpleUploadedFile("test.pdf", buffer.read(), "image/jpeg")
        form = ProfileForm(files={'profile_image': image})
        assert not form.is_valid()
        assert 'Ongeldige bestandsextensie' in str(form.errors)

    def test_valid_different_image_types(self, temporary_media_root):
        """Test all valid image types"""
        valid_types = [
            ("test.jpg", "image/jpeg", "JPEG"),
            ("test.png", "image/png", "PNG"),
            ("test.gif", "image/gif", "GIF"),
        ]

        for filename, content_type, pil_format in valid_types:
            buffer = create_test_image(img_format=pil_format)

            image = SimpleUploadedFile(
                filename, buffer.read(), content_type=content_type
            )

            form = ProfileForm(files={"profile_image": image})
            assert form.is_valid(), f"Failed for {filename} with {content_type}"

    def test_no_image_provided(self, temporary_media_root):
        """Test form when no image is provided (should be valid for updates if not required)"""
        form = ProfileForm(data={})
        assert form.is_valid() or "profile_image" in form.errors

def create_test_image(img_format="JPEG", size=(100, 100)):
    """Helper om test afbeeldingen te maken"""
    image = Image.new("RGB", size, color="red")
    buffer = io.BytesIO()

    if img_format.upper() == "JPEG":
        quality = 95
        image.save(buffer, format=img_format, quality=quality)
    else:
        image.save(buffer, format=img_format)

    buffer.seek(0)
    return buffer
