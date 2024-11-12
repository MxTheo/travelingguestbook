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


class TestObservationFormView:
    """Tests for step 1 observation
    of the multistep form for Non-violent communication compliment"""
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse('step1-observation')

    def test_get_view_renders_formset(self, client):
        """Test if the formset is rendered"""
        response = client.get(self.url)
        assert response.status_code == 200
        assert 'nvc/step1_observation.html' in [t.name for t in response.templates]
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
        assert response.status_code == 200
        assert 'formset' in response.context
        self.assert_formset_error(
            response.context['formset'], 'form-0-observation', 'Ensure this value has at most 255 characters (it has 256).'
            )

    def assert_formset_error(self, formset, field_name, error_message):
        """Helper method to assert formset errors."""
        form = formset.forms[int(field_name.split('-')[1])]
        assert form.errors, f"Expected errors for {field_name} but got none."
        assert error_message in form.errors[field_name.split('-')[1]]
