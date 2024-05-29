from travelingguestbook.factories import GoalFactory, LogMessageFactory, SociableFactory, UserFactory

def test_sociable_factory(sociable_factory):
    assert sociable_factory is SociableFactory

def test_log_message_factory(log_message_factory):
    assert log_message_factory is LogMessageFactory

def test_goal_factory(goal_factory):
    assert goal_factory is GoalFactory

def test_user_factory(user_factory):
    assert user_factory is UserFactory