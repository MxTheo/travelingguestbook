from django.urls import reverse
import pytest
from nvc.forms import ObservationFormSet


def test_observation_formset_valid_data():
    """Prepare valid data for the formset"""
    data = {
        'form-0-observation': 'I heard you say something.',
        'form-1-observation': 'I saw you doing something.',
        'form-2-observation': '',
        'form-3-observation': '',
        'form-4-observation': '',
        'form-5-observation': '',
        'form-6-observation': '',
        'form-TOTAL_FORMS': 7,
        'form-INITIAL_FORMS': 0,
        'form-MAX_NUM_FORMS': 7,
    }

    formset = ObservationFormSet(data=data)
    assert formset.is_valid()
    assert len(formset.forms) == 7  # Ensure we have 7 forms


def test_observation_formset_invalid_data():
    """Prepare invalid data for the formset (e.g., too long observation)"""
    data = {
        'form-0-observation': 'x' * 256,  # Exceeds max_length
        'form-1-observation': 'I saw you doing something.',
        'form-2-observation': '',
        'form-3-observation': '',
        'form-4-observation': '',
        'form-5-observation': '',
        'form-6-observation': '',
        'form-TOTAL_FORMS': 7,
        'form-INITIAL_FORMS': 0,
        'form-MAX_NUM_FORMS': 7,
    }

    formset = ObservationFormSet(data=data)
    assert not formset.is_valid()
    assert 'observation' in formset.errors[0]  # Check for errors in the first form


def test_observation_formset_can_delete():
    """Test that the formset allows deletion"""
    data = {
        'form-0-observation': 'I heard you say something.',
        'form-0-DELETE': 'on',  # Mark the first form for deletion
        'form-1-observation': 'I saw you doing something.',
        'form-TOTAL_FORMS': 2,
        'form-INITIAL_FORMS': 2,
        'form-MAX_NUM_FORMS': 7,
    }

    formset = ObservationFormSet(data=data)
    assert formset.is_valid()
    assert len(formset.forms) == 2  # Ensure we still have 2 forms
    assert formset.cleaned_data[0]['DELETE'] is True  # First form should be marked for deletion


class TestObservationFormView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse('step1-observation')  # Adjust to your URL name

    def test_get_view_renders_formset(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assert 'nvc/step1_observation.html' in [t.name for t in response.templates]  # Adjust to your template name
        assert 'formset' in response.context
        assert isinstance(response.context['formset'], ObservationFormSet)

    def test_post_view_with_valid_data(self, client):
        """Test if it is redirected if data is valid"""
        valid_data = {
        'form-0-observation': 'I heard you say something.',
        'form-1-observation': 'I saw you doing something.',
        'form-2-observation': '',
        'form-3-observation': '',
        'form-4-observation': '',
        'form-5-observation': '',
        'form-6-observation': '',
        'form-TOTAL_FORMS': 7,
        'form-INITIAL_FORMS': 0,
        'form-MAX_NUM_FORMS': 7,
    }
        
        response = client.post(self.url, data=valid_data)
        assert response.status_code == 302
        # You can also add assertions to check if data is processed correctly

    def test_post_view_with_invalid_data(self, client):
        """Test if errors are returned when observation is empty"""
        invalid_data = {
        'form-0-observation': 'x' * 256,  # Exceeds max_length
        'form-1-observation': 'I saw you doing something.',
        'form-2-observation': '',
        'form-3-observation': '',
        'form-4-observation': '',
        'form-5-observation': '',
        'form-6-observation': '',
        'form-TOTAL_FORMS': 7,
        'form-INITIAL_FORMS': 0,
        'form-MAX_NUM_FORMS': 7,
    }
        
        response = client.post(self.url, data=invalid_data)
        assert response.status_code == 200  # Should return to the form with errors
        assert 'formset' in response.context
        self.assert_formset_error(response.context['formset'], 'form-1-observation', 'Exceeds max_length.')

    def assert_formset_error(self, formset, field_name, error_message):
        """Helper method to assert formset errors."""
        form = formset.forms[int(field_name.split('-')[1])]
        assert form.errors, f"Expected errors for {field_name} but got none."
        assert error_message in form.errors[field_name.split('-')[1]]