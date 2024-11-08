

from django import forms
from django.forms import formset_factory
from nvc.forms import ObservationForm, ObservationFormSet  # Adjust the import based on your app structure

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