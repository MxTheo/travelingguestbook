from persona.forms import PersonaForm

class TestForms:
    """Tests for persona forms using factories."""
    def test_persona_form_valid(self):
        """Test valid data for PersonaForm"""
        form_data = {
            'title': 'Test Persona Form',
            'core_question': 'Test question?',
            'description': 'Test description for form',
        }
        form = PersonaForm(data=form_data)
        assert form.is_valid()
    
    def test_persona_form_invalid(self):
        """Test invalid data for PersonaForm"""
        form_data = {
            'title': '',  # Required field
            'core_question': 'Test question?',
            'description': 'Test description',
        }
        form = PersonaForm(data=form_data)
        assert not form.is_valid()
        assert 'title' in form.errors
