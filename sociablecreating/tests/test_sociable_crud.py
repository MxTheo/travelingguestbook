from datetime import date
from django.urls import reverse
from travelingguestbook.factories import LogMessageFactory, SociableFactory, UserFactory
from travelingguestbook.helpers_test import create_logmessage
from sociablecreating.models import LogMessage, Sociable


class TestCreateCode:
    """Test class for the CreateView for Code"""

    def test_if_owner_is_set(self, auto_login_user):
        """Test if the owner is set when creating a code"""
        client, _ = auto_login_user()
        client.post(reverse("create-sociable"))
        list_sociable = Sociable.objects.all()
        assert list_sociable

    def test_if_a_slug_of_5_chars_is_created(self, auto_login_user):
        """Test if a slug is created of 5 chars, when creating a code"""
        client, _ = auto_login_user()
        client.post(reverse("create-sociable"))
        sociable  = Sociable.objects.all()[0]
        assert len(sociable.slug) == 5


class TestDeleteCode:
    """Test user permissions for deleting a code"""

    def test_delete_code_by_different_user(self, auto_login_user):
        """Logged in as a different user then the owner,
        tests if the user is not able to delete the code"""
        client, _ = auto_login_user()
        owner     = UserFactory()
        code      = SociableFactory(owner=owner)

        self.delete_code(client, code)

        assert Sociable.objects.count() == 1

    def test_delete_code_by_owner(self, auto_login_user):
        """Logged in as the owner,
        tests if the owner is able to delete the code"""
        client, owner = auto_login_user()
        code = SociableFactory(owner=owner)

        self.delete_code(client, code)

        assert Sociable.objects.count() == 0

    def test_delete_code_without_authentication(self, client):
        """Not logged in,
        tests if the anonymous user is not able to delete the code"""
        code = SociableFactory()

        self.delete_code(client, code)

        assert Sociable.objects.count() == 1

    def delete_code(self, client, code):
        """Given the client and the code, delete the code"""
        delete_code_url = reverse("delete-sociable", args=[code.slug])
        client.delete(delete_code_url)


class TestDeleteLogMessage:
    """Test user permissions to delete log message"""

    def test_delete_logmessage_by_different_user(self, auto_login_user):
        """Logged in as a different user then the owner of the code,
        tests if the user is not able to delete the logmessage"""
        client, _  = auto_login_user()
        owner      = UserFactory()
        code       = SociableFactory(owner=owner)
        logmessage = LogMessageFactory(sociable=code)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def test_delete_logmessage_by_owner(self, auto_login_user):
        """Logged in as the owner of the code,
        tests if the owner is able to delete the logmessage"""
        client, owner = auto_login_user()
        code          = SociableFactory(owner=owner)
        logmessage    = LogMessageFactory(sociable=code)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 0

    def test_delete_logmessage_without_authentication(self, client):
        """Not logged in,
        tests if the anonymous user is not able to delete the logmessage"""
        code       = SociableFactory()
        logmessage = LogMessageFactory(sociable=code)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def delete_logmessage(self, client, logmessage):
        """Given the client and the logmessage, delete the logmessage"""
        delete_logmessage_url = reverse("delete-logmessage", args=[logmessage.id])
        client.delete(delete_logmessage_url)


class TestCreateLogMessage:
    """Tests for creating logmessage"""

    def test_message_code_relationship_set(self, client):
        """Given a code and creating a logmessage,
        tests if the code relationship is set"""
        code       = SociableFactory()
        logmessage = create_logmessage(client, code)
        assert logmessage.sociable == code

    def test_if_logged_in_user_is_set_as_user(self, auto_login_user):
        """Logged in, tests if the user is set for the logmessage"""
        client, user = auto_login_user()
        logmessage   = create_logmessage(client)
        assert logmessage.author == user

    def test_if_name_is_not_changed_with_anonymous_user(self, client):
        """Not logged in, tests if the name is not altered"""
        logmessage = create_logmessage(
            client, data={"name": "test-name", "body": "test-body", "to_person": "test-to_person"}
        )
        assert logmessage.name == "test-name"

    def test_if_user_is_blank_with_anonymous_user(self, client):
        """Not logged in, tests if the name is not altered"""
        logmessage = create_logmessage(client)
        assert logmessage.author is None

    def test_if_username_is_filled_in_on_form(self, auto_login_user):
        """Logged in, tests if the username is shown in the name field of the form"""
        client, user = auto_login_user()
        code         = SociableFactory()
        url_logmessage_form = reverse("create-logmessage", args=[code.slug])
        response = client.get(url_logmessage_form)
        username = 'value="' + user.username
        assert username in response.rendered_content

    def test_if_anoniem_is_entered_with_anonymous_user(self, client):
        """Not logged in, tests if "Anoniem" is shown in the name field of the form"""
        code     = SociableFactory()
        url_logmessage_form = reverse("create-logmessage", args=[code.slug])
        response = client.get(url_logmessage_form)
        assert 'value="Anoniem' in response.rendered_content


class TestUpdateLogMessage:
    """Test user permissions for updating logmessage"""

    def test_update_logmessage_by_author(self, auto_login_user):
        """Logged in as the author,
        test if the author can update the logmessage"""
        client, author = auto_login_user()
        sociable       = SociableFactory()
        logmessage     = LogMessageFactory(sociable=sociable, author=author)
        logmessage_changed = self.update_logmessage(client, logmessage, "Hello")
        assert logmessage_changed.body == "Hello"
        assert logmessage_changed.date_changed.date() == date.today()

    def test_update_logmessage_by_owner(self, auto_login_user):
        """Logged in as the owner,
        test if the owner can update the logmessage"""
        client, owner = auto_login_user()
        sociable      = SociableFactory(owner=owner)
        logmessage    = LogMessageFactory(sociable=sociable)
        logmessage_changed = self.update_logmessage(client, logmessage, "Hello")
        assert logmessage_changed.body == "Hello"
        assert logmessage_changed.date_changed.date() == date.today()

    def test_update_logmessage_by_anonymous(self, client):
        """Logged in as an anonymous user,
        test if the user cannot update the logmessage"""
        sociable   = SociableFactory()
        logmessage = LogMessageFactory(sociable=sociable)
        logmessage_changed = self.update_logmessage(client, logmessage, "Hello")
        assert logmessage_changed.body != "Hello"
        assert logmessage_changed.date_changed is None

    def update_logmessage(self, client, logmessage, message_body):
        """Given the logmessage and the textbody,
        change the message_body"""
        url_update = reverse("update-logmessage", args=[logmessage.id])
        client.post(url_update, data={"body": message_body, "name": logmessage.name, "to_person": logmessage.to_person})
        return LogMessage.objects.get(id=logmessage.id)


class TestDetailSociable:
    """Tests for DetailView of Sociable"""

    def test_get_context_data(self, client):
        """Test if the detailpage is reached"""
        sociable = SociableFactory(slug="test")
        url      = reverse("detail-sociable", args=[sociable.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert response.context_data["page_url"] == "http://testserver/test/"

    def test_create_createlogmessageurl_for_qr(self, client):
        """Test if the url to creating a logmessage for qr-code is correctly created"""
        sociable = SociableFactory(slug="test")

        response = client.get(reverse("detail-sociable", args=[sociable.slug]))
        qr_url   = response.context["view"].create_createlogmessageurl_for_qr()

        assert qr_url == "http://testserver/nieuwbericht/test"


def test_sociable_absolute_url_with_200(client):
    """Tests if the slug is used as absolute url of the sociable"""
    sociable     = SociableFactory()
    absolute_url = sociable.get_absolute_url()
    assert absolute_url == "/" + str(sociable.slug)
    response     = client.get(absolute_url)
    assert response.status_code == 302
