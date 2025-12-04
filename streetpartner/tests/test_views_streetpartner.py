from tarfile import data_filter
from django.urls import reverse
from travelingguestbook.factories import PartnershipRequestFactory, StreetPartnershipFactory, UserFactory
from streetpartner.models import StreetPartnership
from streetpartner.models import PartnershipRequest

class TestSendPartnershipRequestView:
    """Tests for sending a streetpartnership request"""

    def test_send_valid_request(self, auto_login_user):
        """Given a request to a different user then themself, which is not yet a streetpartner, that is open to a streetpartnership for the first time, tests that the request is made"""
        client, _ = auto_login_user()
        target_user = UserFactory()
        target_user.profile.is_open_for_partnerships = True
        target_user.profile.save()
        url = reverse('request_partnership', kwargs={'username': target_user.username})
        response = client.post(url, data={'message': 'Laten we straatpartners worden!'})
        assert response.status_code == 302

    def test_send_request_to_themself(self, auto_login_user):
        """Given a request to their own account,
        tests if that results in a validation error"""
        client, user = auto_login_user()
        response = client.post(
            reverse('request_partnership', kwargs={'username': user.username}),
            data={}
        )
        assert response.status_code == 200
        assert "Je kunt jezelf niet uitnodigen" in response.content.decode()

    def test_send_request_to_a_partnered_user(self, auto_login_user):
        """Given a request to a user that he is already partnered with,
        tests if that results in a validation error"""
        client, user = auto_login_user()
        target_user = UserFactory(is_open_for_partnerships=True)
        # Create an existing partnership
        StreetPartnershipFactory(user1=user, user2=target_user, is_active=True)
        response = client.post(
            reverse('request_partnership', kwargs={'username': target_user.username}),
            data={}
        )
        assert response.status_code == 200
        assert "Jullie zijn al straatpartners" in response.content.decode()

    def test_send_request_to_a_user_that_is_not_open_for_partnership(self, auto_login_user):
        """Given a request to a user that is not open for partnership,
        tests if that results in a validation error"""
        client, _ = auto_login_user()
        target_user = UserFactory(is_open_for_partnerships=False)
        response = client.post(
            reverse('request_partnership', kwargs={'username': target_user.username}),
            data={}
        )
        assert response.status_code == 200
        assert "Deze gebruiker staat niet open voor nieuwe partners" in response.content.decode()

    def test_send_a_second_request_to_a_user(self, auto_login_user):
        """Given a second request to a user,
        tests if that results in a validation error"""
        client, user = auto_login_user()
        target_user = UserFactory(is_open_for_partnerships=True)
        
        PartnershipRequestFactory(from_user=user, to_user=target_user, status='pending')
        response = client.post(
            reverse('request_partnership', kwargs={'username': target_user.username}),
            data={}
        )
        assert response.status_code == 200
        assert "Er bestaat al een verzoek tussen jullie" in response.content.decode()