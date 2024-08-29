from django.urls import reverse
from conftest import auto_login_user
from travelingguestbook.factories import LogMessageFactory, SociableFactory, UserFactory
from travelingguestbook.helpers_test import create_logmessage, helper_test_page_rendering, create_sociable
from sociablecreating.models import LogMessage, Sociable


class TestCreateSociable:
    '''Test class for the CreateView for Sociable'''
    def test_if_create_sociable_is_rendered(self, auto_login_user):
        '''Test if the create sociable page can be get'''
        client, _ = auto_login_user()
        helper_test_page_rendering(client, 'create-sociable')

    def test_if_owner_is_set(self, auto_login_user):
        '''Test if the owner is set when creating a sociable'''
        client, owner = auto_login_user()
        sociable = create_sociable(client)
        assert sociable.owner == owner

    def test_if_a_slug_of_8_chars_is_created(self, auto_login_user):
        '''Test if a slug is created of 8 chars, when creating a sociable'''
        client, _ = auto_login_user()
        sociable = create_sociable(client)
        assert len(sociable.slug) == 8


class TestUpdateSociable:
    '''Test user permissions for updating the sociable'''
    def test_update_sociable_by_different_user(self, auto_login_user):
        '''Logged in as a different user then the owner,
        tests if that user cannot change the description'''
        client, _ = auto_login_user()
        owner = UserFactory()
        sociable = SociableFactory(owner=owner)

        sociable_changed = self.update_sociable(client, sociable, 'Hello')

        assert sociable_changed.description != 'Hello'

    def test_update_sociable_by_owner(self, auto_login_user):
        '''Logged in as the owner,
        tests if that owner is able to change the description'''
        client, owner = auto_login_user()
        sociable      = SociableFactory(owner=owner)

        sociable_changed = self.update_sociable(client, sociable, 'Hello')

        assert sociable_changed.description == 'Hello'

    def update_sociable(self, client, sociable, description_to_change):
        '''Given the client, sociable and the different description,
        change the description of the sociable'''
        update_sociable_url = reverse('update-sociable', args=[sociable.slug])
        client.post(update_sociable_url, data={'description': description_to_change})
        return Sociable.objects.get(slug=sociable.slug)


class TestDeleteSociable:
    '''Test user permissions for deleting a sociable'''
    def test_delete_sociable_by_different_user(self, auto_login_user):
        '''Logged in as a different user then the owner,
        tests if the user is not able to delete the sociable'''
        client, _ = auto_login_user()
        owner     = UserFactory()
        sociable  = SociableFactory(owner=owner)

        self.delete_sociable(client, sociable)

        assert Sociable.objects.count() == 1

    def test_delete_sociable_by_owner(self, auto_login_user):
        '''Logged in as the owner,
        tests if the owner is able to delete the sociable'''
        client, owner = auto_login_user()
        sociable      = SociableFactory(owner=owner)

        self.delete_sociable(client, sociable)

        assert Sociable.objects.count() == 0

    def test_delete_sociable_without_authentication(self, client):
        '''Not logged in,
        tests if the anonymous user is not able to delete the sociable'''
        sociable = SociableFactory()

        self.delete_sociable(client, sociable)

        assert Sociable.objects.count() == 1

    def delete_sociable(self, client, sociable):
        '''Given the client and the sociable, delete the sociable'''
        delete_sociable_url = reverse('delete-sociable', args=[sociable.slug])
        client.delete(delete_sociable_url)


class TestDeleteLogMessage:
    '''Test user permissions to delete log message'''
    def test_delete_logmessage_by_different_user(self, auto_login_user):
        '''Logged in as a different user then the owner of the sociable,
        tests if the user is not able to delete the logmessage'''
        client, _  = auto_login_user()
        owner      = UserFactory()
        sociable   = SociableFactory(owner=owner)
        logmessage = LogMessageFactory(sociable=sociable)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def test_delete_logmessage_by_owner(self, auto_login_user):
        '''Logged in as the owner of the sociable,
        tests if the owner is able to delete the logmessage'''
        client, owner   = auto_login_user()
        sociable        = SociableFactory(owner=owner)
        logmessage      = LogMessageFactory(sociable=sociable)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 0

    def test_delete_logmessage_without_authentication(self, client):
        '''Not logged in,
        tests if the anonymous user is not able to delete the logmessage'''
        sociable   = SociableFactory()
        logmessage = LogMessageFactory(sociable=sociable)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def delete_logmessage(self, client, logmessage):
        '''Given the client and the logmessage, delete the logmessage'''
        delete_logmessage_url = reverse('delete-logmessage', args=[logmessage.id])
        client.delete(delete_logmessage_url)


class TestCreateLogMessage:
    '''Tests for creating logmessage'''
    def test_message_sociable_relationship_set(self, client):
        '''Given a sociable and creating a logmessage,
        tests if the sociable relationship is set'''
        sociable = SociableFactory()
        logmessage = create_logmessage(client, sociable)
        assert logmessage.sociable == sociable

    def test_if_logged_in_user_is_set_as_user(self, auto_login_user):
        '''Logged in, tests if the user is set for the logmessage'''
        client, user = auto_login_user()
        logmessage = create_logmessage(client)
        assert logmessage.author == user

    def test_if_name_is_not_changed_with_anonymous_user(self, client):
        '''Not logged in, tests if the name is not altered'''
        logmessage = create_logmessage(client, data={'name': 'test-name', 'body': 'test-body'})
        assert logmessage.name == 'test-name'

    def test_if_user_is_blank_with_anonymous_user(self, client):
        '''Not logged in, tests if the name is not altered'''
        logmessage = create_logmessage(client)
        assert logmessage.author is None

    def test_if_username_is_filled_in_on_form(self, auto_login_user):
        '''Logged in, tests if the username is shown in the name field of the form'''
        client, user = auto_login_user()
        sociable = SociableFactory()
        url_logmessage_form = reverse('create-logmessage', args=[sociable.slug])
        response = client.get(url_logmessage_form)
        username = 'value="'+user.username
        assert username in response.rendered_content

    def test_if_anoniem_is_entered_with_anonymous_user(self, client):
        '''Not logged in, tests if "Anoniem" is shown in the name field of the form'''
        sociable = SociableFactory()      
        url_logmessage_form = reverse('create-logmessage', args=[sociable.slug])
        response = client.get(url_logmessage_form)
        assert 'value="Anoniem' in response.rendered_content
