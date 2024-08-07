from travelingguestbook.factories import GoalFactory


def test_goal_str():
    '''Test if the title of the goal is returned'''
    goal = GoalFactory(title='test')
    assert str(goal) == 'test'


def test_goal_get_absolute_url():
    '''Test if the url of the detail page of the goal is returned'''
    goal = GoalFactory()
    assert goal.get_absolute_url() == '/goal/1'
