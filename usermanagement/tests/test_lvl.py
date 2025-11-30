from django.urls import reverse
from django.contrib import auth
from travelingguestbook.factories import StreetActivityFactory, ExperienceFactory
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
    assert profile.xp_next_lvl == 75


class TestLvl:
    """Tests for lvling up
    xp_next_lvl = 75 * lvl ^ 1.5"""

    def test_that_experience_is_added_based_on_confidence_lvl(self, auto_login_user):
        """Given a user of 0xp who describes 1 experience of insecure confidence, test if the user gets 75xp"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        experience = ExperienceFactory()
        data_experience = {
            "report": experience.report,
            "confidence_level": "pioneer",
            "from_practitioner": True,
            "keywords": experience.keywords,
        }
        url = reverse("create-experience", args=[activity.id])

        client.post(url, data_experience, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.xp == 75

    def test_from_lvl_0_to_1_insecure_experience(self, auto_login_user):
        """Given a user of lvl 1 who describes 1 experiences of insecure confidence,
        tests if they lvl up"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        experience = ExperienceFactory()
        data_experience = {
            "report": experience.report,
            "confidence_level": "pioneer",
            "from_practitioner": True,
            "keywords": experience.keywords,
        }
        url = reverse("create-experience", args=[activity.id])

        client.post(url, data_experience, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 212
        assert profile.xp == 75
        assert profile.xp_start == 75

    def test_from_lvl_0_to_1_inbetween_experience(self, auto_login_user):
        """Given a user of lvl 1 describing 2 experiences of inbetween confidence,
        tests if they lvl up"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        experience = ExperienceFactory()
        data_experience = {
            "report": experience.report,
            "confidence_level": "intermediate",
            "from_practitioner": True,
            "keywords": experience.keywords,
        }
        url = reverse("create-experience", args=[activity.id])

        client.post(url, data_experience, follow=True)
        client.post(url, data_experience, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.lvl == 2
        assert profile.xp_next_lvl == 212
        assert profile.xp == 100
        assert profile.xp_start == 75

class TestProgress:
    def test_progress_in_between(self, auto_login_user):
        """Given a user of lvl 1 who describes 1 experiences of inbetween confidence (50xp),
        tests the progress percentage is updated"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        experience = ExperienceFactory()
        data_experience = {
            "report": experience.report,
            "confidence_level": "intermediate",
            "from_practitioner": True,
            "keywords": experience.keywords,
        }
        url = reverse("create-experience", args=[activity.id])

        client.post(url, data_experience, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.xp_percentage_of_progress == 66
        
    def test_progress_lvl_up(self, auto_login_user):
        """Given a user of lvl 1 describing 2 experiences of inbetween confidence (50xp),
        tests if they lvl up"""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        experience = ExperienceFactory()
        data_experience = {
            "report": experience.report,
            "confidence_level": "intermediate",
            "from_practitioner": True,
            "keywords": experience.keywords,
        }
        url = reverse("create-experience", args=[activity.id])

        client.post(url, data_experience, follow=True)
        client.post(url, data_experience, follow=True)

        profile = Profile.objects.get(user=user)
        assert profile.xp_percentage_of_progress == 18