from travelingguestbook.factories import PersonaFactory, ProblemFactory, ReactionFactory

class TestModels:
    """Tests for persona models using factories."""
    def test_persona_creation(self):
        """Test creation of Persona model"""
        persona = PersonaFactory()
        assert persona.title.startswith('Test Persona')
        assert persona.get_absolute_url() is not None
    
    def test_problem_creation(self):
        """Test creation of Problem model"""
        problem = ProblemFactory()
        assert problem.text.startswith('Problem text')
        assert problem.persona is not None
    
    def test_reaction_creation(self):
        """Test creation of Reaction model"""
        reaction = ReactionFactory()
        assert reaction.text.startswith('Reaction text')
        assert reaction.persona is not None
    
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

class TestProblemModel:
    """Tests for Problem model."""
    def test_problem_creation(self):
        """Test creation of Problem model"""
        problem = ProblemFactory()
        assert problem.text.startswith('Problem text')
        assert problem.persona is not None
    
    def test_problem_str(self):
        """Test string representation of Problem model"""
        problem = ProblemFactory(text='Test problem')
        assert 'Test problem' in str(problem)

    def test_problem_ordering(self):
        """Test that problems are ordered by date_added descending"""
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
        assert reaction.text.startswith('Reaction text')
        assert reaction.persona is not None
    
    def test_reaction_str(self):
        """Test string representation of Reaction model"""
        reaction = ReactionFactory(text='Test reaction')
        assert 'Test reaction' in str(reaction)

    def test_reaction_ordering(self):
        """Test that reactions are ordered by date_added descending"""
        persona = PersonaFactory()
        older_reaction = ReactionFactory(persona=persona)
        newer_reaction = ReactionFactory(persona=persona)
        
        reactions = list(persona.reactions.all())
        assert reactions[0] == newer_reaction
        assert reactions[1] == older_reaction
