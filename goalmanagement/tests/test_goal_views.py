from django.urls import reverse
from travelingguestbook.factories import GoalFactory, SociableFactory
from goalmanagement.models import Goal

def test_orders_goal_list_by_count_sociables (client):
    goal_with_2 = GoalFactory(name='2')
    goal_with_1 = GoalFactory(name='1')
    SociableFactory(goal=goal_with_1)
    SociableFactory(goal=goal_with_2)
    SociableFactory(goal=goal_with_2)

    url = reverse('goals')
    client = client.get(url)
    goal_list = list(client.context['goal_list'])
    assert goal_list[0].name == '2'

class TestDeleteGoal:
    def test_delete_goal_by_different_user(self, create_user, auto_login_user):
        client, _ = auto_login_user()
        creator = create_user()
        goal = GoalFactory(creator=creator)

        self.delete_goal(client, goal)

        assert Goal.objects.count() == 1

    def test_delete_goal_by_creator(self, auto_login_user):
        client, creator = auto_login_user()
        goal            = GoalFactory(creator=creator)

        self.delete_goal(client, goal)

        assert Goal.objects.count() == 0

    def test_delete_goal_without_authentication(self, client):
        goal = GoalFactory()

        self.delete_goal(client, goal)

        assert Goal.objects.count() == 1

    def delete_goal(self, client, goal):
        delete_goal_url = reverse('delete-goal', args=[goal.id])
        client.delete(delete_goal_url)