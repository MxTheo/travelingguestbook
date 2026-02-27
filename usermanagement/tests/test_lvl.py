from django.urls import reverse
from django.contrib import auth
from travelingguestbook.factories import StreetActivityFactory, MomentFactory
from usermanagement.models import Profile

def test_registered_user_has_lvl_values_initialized(client):
    """Test if user has lvl values initialized, after succesfull registration"""
    register_url = reverse("register")
    data_correct = {
        "username": "test",
        "email": "test@test.nl",
        "password1": "Pass123!",
        "password2": "Pass123!",
    }
    client.post(register_url, data_correct)
    user = auth.get_user(client)
    profile = Profile.objects.get(user=user)
    assert profile.lvl == 1
    assert profile.xp == 0
    assert profile.xp_start == 0
    assert profile.xp_next_lvl == 100


class TestLvl:
    """Tests for lvling up
    xp_next_lvl = 100 * lvl ^ 1.7"""

    def test_that_moment_is_added(self, auto_login_user):
        """Given a user of 0xp who describes 1 moment, test if the user gets 50xp"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        moment = MomentFactory()
        data_moment = {
            "word": moment.word,
        }
        url = reverse("create-moment", args=[activity.id])

        client.post(url, data_moment, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.xp == 50

    def test_from_lvl_1_to_2(self, auto_login_user):
        """Given a user of lvl 1 who describes 2 moments,
        tests if they lvl up"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        moment = MomentFactory()
        data_moment = {
            "word": moment.word,
        }
        url = reverse("create-moment", args=[activity.id])

        client.post(url, data_moment, follow=True)
        client.post(url, data_moment, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 324
        assert profile.xp == 100
        assert profile.xp_start == 100

class TestProgress:
    """Tests for progress percentage towards next lvl"""
    def test_progress_in_between(self, auto_login_user):
        """Given a user of lvl 1 who describes 1 moment,
        tests the progress percentage is updated"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        moment = MomentFactory()
        data_moment = {
            "word": moment.word,
        }
        url = reverse("create-moment", args=[activity.id])

        client.post(url, data_moment, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.xp_percentage_of_progress == 50
        
    def test_progress_lvl_up(self, auto_login_user):
        """Given a user of lvl 1 describing 2 moments,
        tests if they lvl up"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        moment = MomentFactory()
        data_moment = {
            "report": moment.report,
        }
        url = reverse("create-moment", args=[activity.id])

        client.post(url, data_moment, follow=True)
        client.post(url, data_moment, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.xp_percentage_of_progress == 0