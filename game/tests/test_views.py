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
    lvl^1.2 = xp needed for next lvl'''

    def test_from_lvl_0_to_1(self, auto_login_user):
        '''Given a user of lvl 0 logging their 1st conversation, tests if they goes to lvl 1'''
        client, user = auto_login_user()

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 1
        assert profile.xp_next_lvl == 2
        assert profile.xp == 1
        assert profile.xp_start_lvl == 1

    def test_from_lvl_1_to_2(self, auto_login_user):
        '''Given a user of lvl 1 logging their 4th conversation, tests if they goes to lvl 2'''
        client, user = init_profile(auto_login_user, 1, 1, 2, 1)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 4
        assert profile.xp == 2
        assert profile.xp_start_lvl == 2

    def test_from_lvl_0_to_2_for_loop(self, auto_login_user):
        '''Given a user of lvl 0 logging 5 conversations, tests if they goes to lvl 2
        '''
        client, user = auto_login_user()

        for _ in range(5):
            create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 3
        assert profile.xp_next_lvl == 8
        assert profile.xp == 5
        assert profile.xp_start_lvl == 4

    def test_remain_lvl_2(self, auto_login_user):
        '''Given a user of lvl 2 with 2 logmessage left, tests if they remain at lvl 2'''
        client, user = init_profile(auto_login_user, 2, 2, 4, 2)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 4
        assert profile.xp == 3
        assert profile.xp_start_lvl == 2

    def test_from_lvl_4_to_5(self, auto_login_user):
        '''Given a user of lvl 4 logging their 20th conversation, tests if they lvl up to 5'''
        client, user = init_profile(auto_login_user, 4, 12, 13, 8)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 5
        assert profile.xp_next_lvl == 20
        assert profile.xp == 13
        assert profile.xp_start_lvl == 13

    def test_remain_lvl_4(self, auto_login_user):
        '''Given a user of lvl 4 logging their 12th conversation, tests if they remain at lvl 4'''
        client, user = init_profile(auto_login_user, 4, 11, 13, 8)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 4
        assert profile.xp_next_lvl == 13
        assert profile.xp == 12
        assert profile.xp_start_lvl == 8

    def test_lvl_up_when_logging_on_same_sociable(self, auto_login_user):
        '''Given a user of lvl 4 logging their 13th message on a same sociable,
        tests if they lvl up'''
        client, user = init_profile(auto_login_user, 4, 11, 13, 8)

        sociable = SociableFactory()
        create_logmessage(client, sociable)
        create_logmessage(client, sociable)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 5
        assert profile.xp_next_lvl == 20
        assert profile.xp == 13
        assert profile.xp_start_lvl == 13


class TestCalcPercentageGained:
    '''Tests for calculating the values for the progress bar for lvling up'''
    def test_when_50_percent_to_go(self, auto_login_user):
        '''
        Given a user that is lvl 2, and requires 1 more xp,
        tests if the progress returned is 50%
        '''
        _, user = init_profile(auto_login_user, 2, 3, 4, 2)
        percentage_xp = calc_percentage_xp(user)
        assert percentage_xp == 50

    def test_when_16point66_percent_to_go(self, auto_login_user):
        '''
        Given a user that is lvl 9, and required 2 more xp,
        tests if the progress returned is rounded
        '''
        _, user = init_profile(auto_login_user, 9, 62, 65, 51)
        percentage_xp = calc_percentage_xp(user)
        assert percentage_xp == 79


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
