from django.urls import reverse
from travelingguestbook.factories import GoalFactory, SociableFactory, UserFactory
from goalmanagement.models import Goal
from travelingguestbook.helpers_test import helper_test_page_rendering

def test_orders_goal_list_by_count_sociables (client):
    '''Given a goal with 2 sociables and a goal with 1 sociables,
    test if it returns a list where the goal with 2 sociables is on top'''
    goal_with_2 = GoalFactory(title='2')
    goal_with_1 = GoalFactory(title='1')
    SociableFactory(goal=goal_with_1)
    SociableFactory(goal=goal_with_2)
    SociableFactory(goal=goal_with_2)

    url = reverse('goals')
    client = client.get(url)
    goal_list = list(client.context['goal_list'])
    assert goal_list[0].title == '2'

class TestDeleteGoal:
    '''Tests user permissions for deleting a goal'''
    def test_delete_goal_by_different_user(self, auto_login_user):
        '''Logged in as a user different then the goal creator,
        tests that the user is not able to delete the goal'''
        client, _ = auto_login_user()
        creator = UserFactory()
        goal = GoalFactory(creator=creator)

        self.delete_goal(client, goal)

        assert Goal.objects.count() == 1

    def test_delete_goal_by_creator(self, auto_login_user):
        '''Logged in as the creater,
        tests if the creator is able to delete its own goal'''
        client, creator = auto_login_user()
        goal            = GoalFactory(creator=creator)

        self.delete_goal(client, goal)

        assert Goal.objects.count() == 0

    def test_delete_goal_without_authentication(self, client):
        '''Given no user is logged in,
        tests if the anonymous user is not able to delete the goal'''
        goal = GoalFactory()

        self.delete_goal(client, goal)

        assert Goal.objects.count() == 1

    def delete_goal(self, client, goal):
        '''Given the client and the goal, delete the goal'''
        delete_goal_url = reverse('delete-goal', args=[goal.id])
        client.delete(delete_goal_url)

def test_goal_detail(client):
    '''Test if goal detail page is rendered'''
    goal = GoalFactory()
    helper_test_page_rendering(client, 'goal', [goal.id])