import pytest
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from persona.forms import PersonaForm


class TestForms:
    """Tests for persona forms using factories."""
    def test_persona_form_valid(self):
        """Test valid data for PersonaForm"""
        form_data = {
            "title": "Test Persona Form",
            "core_question": "Test question?",
            "description": "Test description for form",
        }
        form = PersonaForm(data=form_data)
        assert form.is_valid()

    def test_persona_form_invalid(self):
        """Test invalid data for PersonaForm"""
        form_data = {
            "title": "",  # Required field
            "core_question": "Test question?",
            "description": "Test description",
        }
        form = PersonaForm(data=form_data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_form_with_portrait(self, temporary_media_root):
        """Test form with portrait file"""
        image = Image.new("RGB", (100, 100), color="red")
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        mock_image = SimpleUploadedFile(
            "test.jpg", image_file.read(), content_type="image/jpeg"
        )

        form_data = {
            "title": "Test Persona",
            "core_question": "Test question?",
            "description": "Test description",
        }
        files = {"portrait": mock_image}
        form = PersonaForm(data=form_data, files=files)

        assert form.is_valid()
