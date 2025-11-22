from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from travelingguestbook.factories import PersonaFactory, ProblemFactory, ReactionFactory

class TestPersonaModel:
    """Tests for persona models using factories."""

    def test_persona_creation(self):
        """Test creation of Persona model"""
        persona = PersonaFactory()
        assert persona.title.startswith("Test Persona")
        assert persona.get_absolute_url() is not None

    def test_persona_str(self):
        """Test string representation of persona"""
        persona = PersonaFactory(title="test")
        assert str(persona) == "test"

    def test_problem_creation(self):
        """Test creation of Problem model"""
        problem = ProblemFactory()
        assert problem.description.startswith("Problem text")
        assert problem.persona is not None

    def test_persona_with_multiple_problems(self):
        """Test a persona with multiple problems"""
        persona = PersonaFactory()
        problems = ProblemFactory.create_batch(5, persona=persona)

        assert persona.problems.count() == 5
        for i, problem in enumerate(persona.problems.all()):
            assert problem in problems

    def test_persona_with_multiple_reactions(self):
        """Test a persona with multiple reactions"""
        persona = PersonaFactory()
        reactions = ReactionFactory.create_batch(5, persona=persona)

        assert persona.reactions.count() == 5
        for i, reaction in enumerate(persona.reactions.all()):
            assert reaction in reactions

    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        persona = PersonaFactory()

        url = persona.get_absolute_url()
        assert url == reverse('persona-detail', kwargs={'pk': persona.pk})

    def test_portrait_url_without_portrait(self):
        """Test portrait_url property when no portrait is set"""
        persona = PersonaFactory(portrait=None)
        assert persona.portrait_url == '/static/persona/images/empty_portrait.jpg'

    def test_portrait_url_with_portrait(self):
        """Test portrait_url property when portrait is set"""
        # Create a simple mock image
        mock_image = SimpleUploadedFile(
            "test.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        persona = PersonaFactory(portrait=mock_image)

        assert not persona.portrait_url == '/static/persona/images/empty_portrait.jpg'

class TestProblemModel:
    """Tests for Problem model."""

    def test_problem_creation(self):
        """Test creation of Problem model"""
        problem = ProblemFactory()
        assert problem.description.startswith("Problem text")
        assert problem.persona is not None

    def test_problem_str(self):
        """Test string representation of Problem model"""
        problem = ProblemFactory(description="Test problem")
        assert "Test problem" in str(problem)

    def test_problem_ordering(self):
        """Test that problems are ordered by date_created descending"""
        persona = PersonaFactory()
        older_problem = ProblemFactory(persona=persona)
        newer_problem = ProblemFactory(persona=persona)

        problems = list(persona.problems.all())
        assert problems[0] == newer_problem
        assert problems[1] == older_problem


class TestReactionModel:
    """Tests for Reaction model."""

    def test_reaction_creation(self):
        """Test creation of Reaction model"""
        reaction = ReactionFactory()
        assert reaction.description.startswith("Reaction text")
        assert reaction.persona is not None

    def test_reaction_str(self):
        """Test string representation of Reaction model"""
        reaction = ReactionFactory(description="Test reaction")
        assert "Test reaction" in str(reaction)

    def test_reaction_ordering(self):
        """Test that reactions are ordered by date_created   descending"""
        persona = PersonaFactory()
        older_reaction = ReactionFactory(persona=persona)
        newer_reaction = ReactionFactory(persona=persona)

        reactions = list(persona.reactions.all())
        assert reactions[0] == newer_reaction
        assert reactions[1] == older_reaction
