from travelingguestbook.factories import SociableFactory
from travelingguestbook.helpers_test import create_logmessage
from usermanagement.models import Profile


class TestLvl:
    '''Tests for lvling up
    3 + lvl = xp needed'''
    def init_profile(self, auto_login_user, lvl, xp_needed):
        '''Initialises a profile for the tests'''
        client, user = auto_login_user()
        profile = Profile.objects.get(user=user)
        profile.lvl = lvl
        profile.xp_needed = xp_needed
        profile.save()
        return client, user

    def test_from_lvl_0_to_1(self, auto_login_user):
        '''Given a user of lvl 0 logging their 1st conversation, tests if they goes to lvl 1'''
        client, user = auto_login_user()

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 1
        assert profile.xp_needed == 4

    def test_from_lvl_1_to_2(self, auto_login_user):
        '''Given a user of lvl 1 logging their 4th conversation, tests if they goes to lvl 2'''
        client, user = self.init_profile(auto_login_user, 1, 1)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_needed == 5

    def test_from_lvl_1_to_2_for_loop(self, auto_login_user):
        '''Given a user of lvl 1 logging 5 conversations, tests if they goes to lvl 2'''
        client, user = self.init_profile(auto_login_user, 0, 1)

        for _ in range(5):
            create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_needed == 5

    def test_remain_lvl_1(self, auto_login_user):
        '''Given a user of lvl 1 with 2 logmessage left, tests if they remain at lvl 1'''
        client, user = self.init_profile(auto_login_user, 1, 2)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 1
        assert profile.xp_needed == 1

    def test_from_lvl_4_to_5(self, auto_login_user):
        '''Given a user of lvl 4 logging their 21th conversation, tests if they remain at lvl 5'''
        client, user = self.init_profile(auto_login_user, 4, 1)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 5
        assert profile.xp_needed == 8

    def test_remain_lvl_4(self, auto_login_user):
        '''Given a user of lvl 4 logging their 20th conversation, tests if they remain at lvl 4'''
        client, user = self.init_profile(auto_login_user, 4, 2)

        create_logmessage(client)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 4
        assert profile.xp_needed == 1

    def test_remain_lvl_4_when_logging_on_same_sociable(self, auto_login_user):
        '''Given a user of lvl 4 logging their 21th message on a same sociable,
        tests if they remain at lvl 4'''
        client, user = self.init_profile(auto_login_user, 4, 2)

        sociable = SociableFactory()
        create_logmessage(client, sociable)
        create_logmessage(client, sociable)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 4
        assert profile.xp_needed == 1
