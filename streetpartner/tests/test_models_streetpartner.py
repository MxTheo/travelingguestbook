import datetime
from freezegun import freeze_time
from streetpartner.models import StreetPartnership
from travelingguestbook.factories import PartnershipRequestFactory, StreetPartnershipFactory, UserFactory

@freeze_time("2024-01-01 12:00:00")
class TestPartnershipRequest:
    """Test for PartnershipRequest model using factories with now on 1-1-2025."""

    def test_expires_at(self):
        """Given a partnershiprequest created at 1 january 2024,
        test if the expires at is at 15 january"""
        partnershiprequest = PartnershipRequestFactory()
        assert partnershiprequest.expires_at == datetime.datetime(2024, 1, 15, 12, 0, tzinfo=datetime.timezone.utc)

    def test_is_expired(self):
        """Given a partnershiprequest is expired by 1 day,
        tests if is_expired returns true"""
        partnershiprequest = PartnershipRequestFactory()
        freezer = freeze_time("2024-01-16 12:00:00")
        freezer.start()
        assert partnershiprequest.is_expired()
        freezer.stop()

    def test_can_accept_is_false(self):
        """Given a partnershiprequest is expired by 1 day,
        tests if request cannot be accepted"""
        partnershiprequest = PartnershipRequestFactory()
        freezer = freeze_time("2024-01-16 12:00:00")
        freezer.start()
        assert not partnershiprequest.can_accept()
        freezer.stop()

    def test_cannot_accept_cancelled(self):
        """Given a partnershiprequest is cancelled,
        tests if request cannot be accepted"""
        cancelled_partnershiprequest = PartnershipRequestFactory(status='cancelled')
        assert not cancelled_partnershiprequest.can_accept()

    def test_str(self):
        """Test the string representation"""
        from_user = UserFactory(username='test1')
        to_user = UserFactory(username='test2')
        partnershiprequest = PartnershipRequestFactory(from_user=from_user, to_user=to_user)
        assert str(partnershiprequest) == "Partnerverzoek van test1 naar test2"

class TestStreetPartnership:
    """Tests for the model StreetPartnership"""
    def setup_method(self):
        """Setup data with user1, user2 and their streetpartnership"""
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.streetpartnership = StreetPartnershipFactory(user1=self.user1, user2=self.user2)

    def test_partners(self):
        """Given user1 and user2 of a streetpartnership,
        tests if partners return both users"""
        assert self.streetpartnership.partners == [self.user1, self.user2]

    def test_get_partner(self):
        """Given user1 and user 2 of a streetpartnership,
        tests if user1 gets partner user2 and user2 gets partner user1"""
        assert self.streetpartnership.get_partner(self.user1) == self.user2
        assert self.streetpartnership.get_partner(self.user2) == self.user1

    def test_get_partner_from_user_that_is_not_a_partner(self):
        """Given user3 that is not part of the partnership,
        tests if no partner is returned"""
        user3 = UserFactory()
        assert not self.streetpartnership.get_partner(user3)

    @freeze_time("2024-01-01 12:00:00")
    def test_end_partnership(self):
        """Given an active partnership,
        tests if it can be deactivated and the time is set correctly"""
        self.streetpartnership.end_partnership()
        assert not self.streetpartnership.is_active
        assert self.streetpartnership.ended_at == datetime.datetime(
            2024, 1, 1, 12, 0, 0,
            tzinfo=datetime.timezone.utc)

    def test_get_partnership(self):
        """Given user1 and user2,
        tests if their streetpartnership can be retrieved"""
        returned_partnership = StreetPartnership.get_partnership(self.user1, self.user2)
        assert returned_partnership == self.streetpartnership

    def test_get_partnership_that_does_not_exist(self):
        """Given user1 and user3 with no partnership,
        tests if no partnership is returned"""
        user3 = UserFactory()
        returned_partnership = StreetPartnership.get_partnership(self.user1, user3)
        assert not returned_partnership

    def test_str(self):
        """Test the string representation"""
        assert str(self.streetpartnership) == f"Partnerschap tussen {self.user1} en {self.user2}" 