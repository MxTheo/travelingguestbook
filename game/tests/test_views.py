from django.urls import reverse
from django.contrib import auth
from game.views import calc_percentage_xp
from travelingguestbook.factories import SociableFactory
from travelingguestbook.helpers_test import create_logmessage
from usermanagement.models import Profile

def init_profile(auto_login_user, lvl, xp, xp_next_lvl, xp_start_lvl):
    '''Initialises a profile for the tests'''
    client, user = auto_login_user()
    profile = Profile.objects.get(user=user)
    profile.lvl = lvl
    profile.xp = xp
    profile.xp_next_lvl = xp_next_lvl
    profile.xp_start_lvl = xp_start_lvl
    profile.save()
    return client, user

class TestLvl:
    '''Tests for lvling up
    3 + lvl = xp needed'''

    def test_from_lvl_0_to_1(self, auto_login_user):
        '''Given a user of lvl 0 logging their 1st conversation, tests if they goes to lvl 1'''
        client, user = auto_login_user()

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 1
        assert profile.xp_next_lvl == 5
        assert profile.xp == 1
        assert profile.xp_start_lvl == 1

    def test_from_lvl_1_to_2(self, auto_login_user):
        '''Given a user of lvl 1 logging their 4th conversation, tests if they goes to lvl 2'''
        client, user = init_profile(auto_login_user, 1, 4, 5, 1)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 10
        assert profile.xp == 5
        assert profile.xp_start_lvl == 5

    def test_from_lvl_0_to_2_for_loop(self, auto_login_user):
        '''Given a user of lvl 0 logging 5 conversations, tests if they goes to lvl 2'''
        client, user = auto_login_user()

        for _ in range(5):
            create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 10
        assert profile.xp == 5
        assert profile.xp_start_lvl == 5

    def test_remain_lvl_1(self, auto_login_user):
        '''Given a user of lvl 1 with 2 logmessage left, tests if they remain at lvl 1'''
        client, user = init_profile(auto_login_user, 1, 2, 5, 1)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 1
        assert profile.xp_next_lvl == 5
        assert profile.xp == 3
        assert profile.xp_start_lvl == 1

    def test_from_lvl_4_to_5(self, auto_login_user):
        '''Given a user of lvl 4 logging their 21th conversation, tests if they remain at lvl 5'''
        client, user = init_profile(auto_login_user, 4, 22, 23, 16)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 5
        assert profile.xp_next_lvl == 31
        assert profile.xp == 23
        assert profile.xp_start_lvl == 23

    def test_remain_lvl_4(self, auto_login_user):
        '''Given a user of lvl 4 logging their 20th conversation, tests if they remain at lvl 4'''
        client, user = init_profile(auto_login_user, 4, 20, 23, 16)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 4
        assert profile.xp_next_lvl == 23
        assert profile.xp == 21
        assert profile.xp_start_lvl == 16

    def test_remain_lvl_4_when_logging_on_same_sociable(self, auto_login_user):
        '''Given a user of lvl 4 logging their 21th message on a same sociable,
        tests if they remain at lvl 4'''
        client, user = init_profile(auto_login_user, 4, 21, 23, 16)

        sociable = SociableFactory()
        create_logmessage(client, sociable)
        create_logmessage(client, sociable)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 4
        assert profile.xp_next_lvl == 23
        assert profile.xp == 22
        assert profile.xp_start_lvl == 16

    # def test_lvl_up_when_more_xp_then_needed(self, auto_login_user):


class TestCalcPercentageGained:
    '''Tests for calculating the values for the progress bar for lvling up'''
    def test_when_50_percent_to_go(self, auto_login_user):
        '''
        Given a user that is lvl 1, and requires 2 more xp,
        tests if the progress returned is 50%
        '''
        _, user = init_profile(auto_login_user, 1, 3, 5, 1)
        percentage_xp = calc_percentage_xp(user)
        assert percentage_xp == 50

    def test_when_16point66_percent_to_go(self, auto_login_user):
        '''
        Given a user that is lvl 9, and required 2 more xp,
        tests if the progress returned is 83% and not 83,33
        '''
        _, user = init_profile(auto_login_user, 9, 71, 73, 61)
        percentage_xp = calc_percentage_xp(user)
        assert percentage_xp == 83


def test_registered_user_has_lvl_values_initialized(client):
    '''Test if user has lvl values initialized, after succesfull registration'''
    register_url = reverse('register')
    data_correct = {'username': 'test', 'email': 'test@test.nl', 'password1': 'Pass123!', 'password2': 'Pass123!'}
    client.post(register_url, data_correct)
    user = auth.get_user(client)
    profile = Profile.objects.get(user=user)
    assert profile.lvl == 0
    assert profile.xp == 0
    assert profile.xp_start_lvl == 0
    assert profile.xp_next_lvl == 1
