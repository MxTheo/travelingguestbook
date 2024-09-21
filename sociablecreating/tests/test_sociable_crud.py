from usermanagement.models import Profile
from django.urls import reverse
from travelingguestbook.factories import LogMessageFactory, ProfileFactory, SociableFactory, UserFactory
from travelingguestbook.helpers_test import create_logmessage, helper_test_page_rendering, create_sociable
from sociablecreating.models import LogMessage, Sociable


class TestCreateCode:
    '''Test class for the CreateView for Code'''
    def test_if_create_code_is_rendered(self, auto_login_user):
        '''Test if the create code page can be get'''
        client, _ = auto_login_user()
        helper_test_page_rendering(client, 'create-sociable')

    def test_if_owner_is_set(self, auto_login_user):
        '''Test if the owner is set when creating a code'''
        client, owner = auto_login_user()
        code = create_sociable(client)
        assert code.owner == owner

    def test_if_a_slug_of_8_chars_is_created(self, auto_login_user):
        '''Test if a slug is created of 8 chars, when creating a code'''
        client, _ = auto_login_user()
        code = create_sociable(client)
        assert len(code.slug) == 8

    def test_if_custom_description_is_used_as_initial_value(self, auto_login_user):
        '''Test if the description the user made itself is used as initial value,
        when creating a code'''
        client, user = auto_login_user()
        custom_descr = 'Test123'
        Profile.objects.get(user=user).delete()
        ProfileFactory(user=user, custom_description_for_code=custom_descr)
        response = client.get('/create-sociable/')
        assert custom_descr in str(response.content)

    def test_if_default_description_is_used_as_initial_value_with_only_whitespaces(self, auto_login_user):
        '''Test if the default description is used, when the user entered only spaces in the custom description,
        when creating a code'''
        client, user = auto_login_user()
        custom_descr = '    '
        Profile.objects.get(user=user).delete()
        ProfileFactory(user=user, custom_description_for_code=custom_descr)
        response = client.get('/create-sociable/')
        assert 'Ik heb een bericht voor je achter gelaten.' in str(response.content)

    def test_if_changed_description_is_used_with_custom_description(self, auto_login_user):
        '''Test if the description can be changed when the user also has a custom description, when creating a code'''
        client, user = auto_login_user()
        Profile.objects.get(user=user).delete()
        ProfileFactory(user=user, custom_description_for_code='test')
        changed_description = 'changed'
        client.post('/create-sociable/', data={'description': changed_description})
        code = Sociable.objects.all()[0]
        assert code.description == changed_description

    def test_if_description_is_saved_as_default(self, auto_login_user):
        '''Test if the description is saved as default, when the user wants to'''
        client, user = auto_login_user()
        description = 'test'
        client.post('/create-sociable/', data={'description': description, 'is_default_description': True})
        profile = Profile.objects.get(user=user)
        assert profile.custom_description_for_code == description

    def test_if_description_is_not_saved_as_default(self, auto_login_user):
        '''Test if the description is not saved as default, when the user leaves it unchecked'''
        client, user = auto_login_user()
        description = 'test'
        client.post('/create-sociable/', data={'description': description, 'is_default_description': False})
        profile = Profile.objects.get(user=user)
        assert profile.custom_description_for_code != description


class TestUpdateCode:
    '''Test user permissions for updating the code'''
    def test_update_code_by_different_user(self, auto_login_user):
        '''Logged in as a different user then the owner,
        tests if that user cannot change the description'''
        client, _ = auto_login_user()
        owner = UserFactory()
        code = SociableFactory(owner=owner)

        code_changed = self.update_code(client, code, 'Hello')

        assert code_changed.description != 'Hello'

    def test_update_code_by_owner(self, auto_login_user):
        '''Logged in as the owner,
        tests if that owner is able to change the description'''
        client, owner = auto_login_user()
        code      = SociableFactory(owner=owner)

        code_changed = self.update_code(client, code, 'Hello')

        assert code_changed.description == 'Hello'

    def update_code(self, client, code, description_to_change):
        '''Given the client, code and the different description,
        change the description of the code'''
        update_code_url = reverse('update-sociable', args=[code.slug])
        client.post(update_code_url, data={'description': description_to_change})
        return Sociable.objects.get(slug=code.slug)


class TestDeleteCode:
    '''Test user permissions for deleting a code'''
    def test_delete_code_by_different_user(self, auto_login_user):
        '''Logged in as a different user then the owner,
        tests if the user is not able to delete the code'''
        client, _ = auto_login_user()
        owner     = UserFactory()
        code  = SociableFactory(owner=owner)

        self.delete_code(client, code)

        assert Sociable.objects.count() == 1

    def test_delete_code_by_owner(self, auto_login_user):
        '''Logged in as the owner,
        tests if the owner is able to delete the code'''
        client, owner = auto_login_user()
        code      = SociableFactory(owner=owner)

        self.delete_code(client, code)

        assert Sociable.objects.count() == 0

    def test_delete_code_without_authentication(self, client):
        '''Not logged in,
        tests if the anonymous user is not able to delete the code'''
        code = SociableFactory()

        self.delete_code(client, code)

        assert Sociable.objects.count() == 1

    def delete_code(self, client, code):
        '''Given the client and the code, delete the code'''
        delete_code_url = reverse('delete-sociable', args=[code.slug])
        client.delete(delete_code_url)


class TestDeleteLogMessage:
    '''Test user permissions to delete log message'''
    def test_delete_logmessage_by_different_user(self, auto_login_user):
        '''Logged in as a different user then the owner of the code,
        tests if the user is not able to delete the logmessage'''
        client, _  = auto_login_user()
        owner      = UserFactory()
        code   = SociableFactory(owner=owner)
        logmessage = LogMessageFactory(sociable=code)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def test_delete_logmessage_by_owner(self, auto_login_user):
        '''Logged in as the owner of the code,
        tests if the owner is able to delete the logmessage'''
        client, owner   = auto_login_user()
        code        = SociableFactory(owner=owner)
        logmessage      = LogMessageFactory(sociable=code)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 0

    def test_delete_logmessage_without_authentication(self, client):
        '''Not logged in,
        tests if the anonymous user is not able to delete the logmessage'''
        code   = SociableFactory()
        logmessage = LogMessageFactory(sociable=code)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def delete_logmessage(self, client, logmessage):
        '''Given the client and the logmessage, delete the logmessage'''
        delete_logmessage_url = reverse('delete-logmessage', args=[logmessage.id])
        client.delete(delete_logmessage_url)


class TestCreateLogMessage:
    '''Tests for creating logmessage'''
    def test_message_code_relationship_set(self, client):
        '''Given a code and creating a logmessage,
        tests if the code relationship is set'''
        code = SociableFactory()
        logmessage = create_logmessage(client, code)
        assert logmessage.sociable == code

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
        code = SociableFactory()
        url_logmessage_form = reverse('create-logmessage', args=[code.slug])
        response = client.get(url_logmessage_form)
        username = 'value="'+user.username
        assert username in response.rendered_content

    def test_if_anoniem_is_entered_with_anonymous_user(self, client):
        '''Not logged in, tests if "Anoniem" is shown in the name field of the form'''
        code = SociableFactory()      
        url_logmessage_form = reverse('create-logmessage', args=[code.slug])
        response = client.get(url_logmessage_form)
        assert 'value="Anoniem' in response.rendered_content
