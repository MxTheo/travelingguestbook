from django.urls import reverse
from travelingguestbook.factories import PersonaFactory

class TestPersonaProblemReactionIntegration:
    """Integration tests for Persona, Problem, and Reaction models."""
    def test_complete_flow(self, client):
        """Test creating a persona, adding problems and reactions, and viewing details."""
        # Create a persona
        persona = PersonaFactory()

        # Add a problem
        problem_url = reverse('create-problem', kwargs={'persona_pk': persona.pk})
        problem_data = {'text': 'Integration test problem'}
        response = client.post(problem_url, problem_data)
        assert response.status_code == 302
        assert persona.problems.count() == 1

        # Add a reaction
        reaction_url = reverse('create-reaction', kwargs={'persona_pk': persona.pk})
        reaction_data = {'text': 'Integration test reaction'}
        response = client.post(reaction_url, reaction_data)
        assert response.status_code == 302
        assert persona.reactions.count() == 1

        # Check persona detail page
        detail_url = reverse('persona-detail', kwargs={'pk': persona.pk})
        response = client.get(detail_url)
        assert response.status_code == 200
        assert 'Integration test problem' in response.content.decode()
        assert 'Integration test reaction' in response.content.decode()
