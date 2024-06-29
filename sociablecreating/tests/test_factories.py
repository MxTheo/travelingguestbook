from travelingguestbook.factories import GoalFactory, LogMessageFactory,SociableFactory,UserFactory

def test_sociable_factory(sociable_factory):
    '''Tests if sociable_factory is of type SociableFactory'''
    assert sociable_factory is SociableFactory

def test_log_message_factory(log_message_factory):
    '''Tests if log_message_factory is of type LogMessageFactory'''
    assert log_message_factory is LogMessageFactory

def test_goal_factory(goal_factory):
    '''Tests if goal_factory is of type GoalFactory'''
    assert goal_factory is GoalFactory

def test_user_factory(user_factory):
    '''Tests if user_factory is of type UserFactory'''
    assert user_factory is UserFactory
