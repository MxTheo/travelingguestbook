from datetime import date
from django.urls import reverse
from travelingguestbook.factories import LogMessageFactory, SociableFactory
from travelingguestbook.helpers_test import create_logmessage
from sociablecreating.models import LogMessage, Sociable


class TestCreateSociable:
    """Test class for the CreateView for Sociable"""

    def test_if_owner_is_set(self, auto_login_user):
        """Test if the owner is set when creating a sociable"""
        client, _ = auto_login_user()
        client.post(reverse("create-sociable"))
        list_sociable = Sociable.objects.all()
        assert list_sociable

    def test_if_a_slug_of_5_chars_is_created(self, auto_login_user):
        """Test if a slug is created of 5 chars, when creating a sociable"""
        client, _ = auto_login_user()
        client.post(reverse("create-sociable"))
        sociable  = Sociable.objects.all()[0]
        assert len(sociable.slug) == 7

    def test_number_1(self, auto_login_user):
        """Test if number 1 is set for the first sociable"""
        client, _ = auto_login_user()
        client.post(reverse("create-sociable"))
        sociable  = Sociable.objects.all()[0]
        assert sociable.number == 1

    def test_number_3(self, auto_login_user):
        """Test if number 3 is set for the third sociable"""
        client, _ = auto_login_user()
        for _ in range(3):
            client.post(reverse("create-sociable"))
        sociable  = Sociable.objects.all()[0]
        assert sociable.number == 3

    def test_number_with_delete_last(self, auto_login_user):
        """Test if number 3 is set, when 3 are created, the last is deleted and then the sociable is created"""
        client, _ = auto_login_user()
        for _ in range(3):
            client.post(reverse("create-sociable"))
        slug = Sociable.objects.all()[0].slug
        client.post(reverse("delete-sociable", args=[slug]))
        client.post(reverse("create-sociable"))
        sociable = Sociable.objects.all()[0]
        assert sociable.number == 3

    def test_number_with_delete_in_middle(self, auto_login_user):
        """Test if number 3 is set, when 3 are created, the second is deleted and then the sociable is created"""
        client, _ = auto_login_user()
        for _ in range(3):
            client.post(reverse("create-sociable"))
        slug = Sociable.objects.all()[1].slug
        client.post(reverse("delete-sociable", args=[slug]))
        client.post(reverse("create-sociable"))
        sociable = Sociable.objects.all()[0]
        assert sociable.number == 4

    def test_number_3_with_other_sociables(self, auto_login_user):
        """Test if number 3 is set for the third sociable, when there are also other sociables"""
        for _ in range(3):
            SociableFactory()
        client, _ = auto_login_user()
        for _ in range(3):
            client.post(reverse("create-sociable"))
        sociable  = Sociable.objects.all()[0]
        assert sociable.number == 3


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

    def test_if_logged_in_user_is_set_as_user(self, auto_login_user):
        """Logged in, tests if the user is set for the logmessage"""
        client, user = auto_login_user()
        logmessage   = create_logmessage(client)
        assert logmessage.author == user

    def test_if_name_is_not_changed_with_anonymous_user(self, client):
        """Not logged in, tests if the name is not altered"""
        logmessage = create_logmessage(
            client, data={"name": "test-name", "body": "test-body"}
        )
        assert logmessage.name == "test-name"

    def test_if_user_is_blank_with_anonymous_user(self, client):
        """Not logged in, tests if the name is not altered"""
        logmessage = create_logmessage(client)
        assert logmessage.author is None

    def test_if_username_is_filled_in_on_form(self, auto_login_user):
        """Logged in, tests if the username is shown in the name field of the form"""
        client, user = auto_login_user()
        sociable         = SociableFactory()
        url_logmessage_form = reverse("create-logmessage", args=[sociable.slug])
        response = client.get(url_logmessage_form)
        username = 'value="' + user.username
        assert username in response.rendered_content


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
        url      = reverse("detail-sociable", args=[sociable.slug])
        response = client.get(url)

        assert response.status_code == 200


def test_sociable_absolute_url_with_200(client):
    """Tests if the slug is used as absolute url of the sociable"""
    sociable     = SociableFactory()
    absolute_url = sociable.get_absolute_url()
    assert absolute_url == "/c/" + str(sociable.slug)
    response     = client.get(absolute_url)
    assert response.status_code == 302
