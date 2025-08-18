from datetime import date
from django.urls import reverse
from travelingguestbook.factories import LogMessageFactory, SociableFactory
from travelingguestbook.helpers_test import create_logmessage
from sociablecreating.models import LogMessage, Sociable


def test_create_sociable_view(client):
    '''Test the create_sociable view to ensure it creates a Sociable object and redirects correctly.'''
    url = reverse('create-sociable')  # pas aan naar jouw url name
    
    # Doe een POST request naar de view
    response = client.post(url)
    
    # Check dat het antwoord een redirect is (statuscode 302)
    assert response.status_code == 302
    
    # Check dat er een Sociable object is aangemaakt
    assert Sociable.objects.exists()
    
    # Check dat de redirect locatie de detail url is van het gemaakte object
    sociable = Sociable.objects.first()
    assert len(sociable.slug) == 7  # Controleer of de slug correct is aangemaakt
    expected_url = reverse('sociable', args=[sociable.slug])
    assert response.url == expected_url

class TestDeleteSociable:
    """Test user permissions for deleting a sociable"""

    def test_delete_sociable_without_authentication(self, client):
        """Not logged in,
        tests if the anonymous user is able to delete the sociable"""
        sociable = SociableFactory()

        delete_sociable_url = reverse("delete-sociable", args=[sociable.slug])
        client.delete(delete_sociable_url)

        assert Sociable.objects.count() == 0


class TestDeleteLogMessage:
    """Test user permissions to delete log message"""

    def test_delete_logmessage_without_authentication(self, client):
        """Not logged in,
        tests if the anonymous user is able to delete the logmessage"""
        sociable       = SociableFactory()
        logmessage = LogMessageFactory(sociable=sociable)

        delete_logmessage_url = reverse("delete-logmessage", args=[logmessage.id])
        client.delete(delete_logmessage_url)

        assert LogMessage.objects.count() == 0


class TestCreateLogMessage:
    """Tests for creating logmessage"""

    def test_message_sociable_relationship_set(self, client):
        """Given a sociable and creating a logmessage,
        tests if the sociable relationship is set"""
        sociable       = SociableFactory()
        logmessage = create_logmessage(client, sociable)
        assert logmessage.sociable == sociable

    def test_if_name_is_not_changed_with_anonymous_user(self, client):
        """Not logged in, tests if the name is not altered"""
        logmessage = create_logmessage(
            client, data={"name": "test-name", "body": "test-body"}
        )
        assert logmessage.name == "test-name"

class TestUpdateLogMessage:
    """Test user permissions for updating logmessage"""

    def test_update_logmessage_by_anonymous(self, client):
        """Logged in as an anonymous user,
        test if the user cannot update the logmessage"""
        sociable   = SociableFactory()
        logmessage = LogMessageFactory(sociable=sociable)
        logmessage_changed = self.update_logmessage(client, logmessage, "Hello")
        assert logmessage_changed.body == "Hello"
        assert logmessage_changed.date_changed.date() == date.today()

    def update_logmessage(self, client, logmessage, message_body):
        """Given the logmessage and the textbody,
        change the message_body"""
        url_update = reverse("update-logmessage", args=[logmessage.id])
        client.post(url_update, data={"body": message_body, "name": logmessage.name})
        return LogMessage.objects.get(id=logmessage.id)


class TestDetailSociable:
    """Tests for DetailView of Sociable"""

    def test_detail_page(self, client):
        """Test if the detailpage is reached"""
        sociable = SociableFactory(slug="test")
        url      = reverse("sociable", args=[sociable.slug])
        response = client.get(url)

        assert response.status_code == 200


def test_sociable_absolute_url_with_200(client):
    """Tests if the slug is used as absolute url of the sociable"""
    sociable     = SociableFactory()
    absolute_url = sociable.get_absolute_url()
    assert absolute_url == "/c/" + str(sociable.slug)+'/'
    response     = client.get(absolute_url)
    assert response.status_code == 200
