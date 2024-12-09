from django.urls import reverse
import pytest
from travelingguestbook.factories import LogMessageFactory, SociableFactory, UserFactory
from sociablecreating.models import Sociable, LogMessage
from sociablecreating.views import get_sociables_for_dashboard


class TestSearchSociable:
    '''Test the behaviour of search_sociable'''
    url = reverse('search-sociable')

    def test_search_with_correct_slug(self, client):
        '''Given correct slug,
        tests if it returns the page with the sociable'''
        SociableFactory(slug='test123')
        response = client.get(self.url, {'search-code': 'test123'})
        assert response.status_code == 302
        assert 'test123' in response.url

    def test_search_with_slug_with_capital(self, client):
        '''Given a slug with a capital,
        tests if it returns the page with the sociable'''
        SociableFactory(slug='test123')
        response = client.get(self.url, {'search-code': 'Test123'})
        assert response.status_code == 302
        assert 'test123' in response.url

    def test_search_with_incorrect_slug(self, client):
        '''Given incorrect slug,
        tests if it returns Not Found'''
        SociableFactory(slug='test123')
        response = client.get(self.url, {'search-code': 'test456'})
        assert b'niet gevonden' in response.content
        assert response.status_code == 200

    def test_search_with_no_slug(self, client):
        '''Given empty slug,
        tests if it returns Not Found

        A user cannot enter None.
        Even when the user presses enter, the search-code will not be none, but an empty string.
        Therefore, input None will not work and is not tested'''
        SociableFactory(slug='test123')
        response = client.get(self.url, {'search-code': ''})
        assert b'niet gevonden' in response.content
        assert response.status_code == 200

    def test_show_unread_message(self, client):
        '''Given a slug and an unread message,
        tests if the unread message is displayed'''
        sociable   = SociableFactory(slug='test123')
        LogMessageFactory(sociable=sociable)
        response   = client.get(self.url, {'search-code': sociable.slug})
        assert response.status_code == 200

    def test_show_detailpage_when_message_is_read(self, client):
        '''Given a slug and a read message,
        tests if the detailpage is displayed'''
        sociable   = SociableFactory(slug='test123')
        LogMessageFactory(sociable=sociable, is_read=True)
        response   = client.get(self.url, {'search-code': sociable.slug})
        assert response.status_code == 302
        assert 'test123' in response.url

    def test_show_message_when_user_is_owner(self,  auto_login_user):
        '''Given that the visitor is the owner,
        tests if the unread message written by somebody else is still shown'''
        client, user = auto_login_user()
        sociable     = SociableFactory(slug='test123', owner=user)
        LogMessageFactory(sociable=sociable)
        response     = client.get(self.url, {'search-code': sociable.slug})
        assert response.status_code == 200

    def test_show_sociable_when_user_is_author(self,  auto_login_user):
        '''Given that the visitor is the author, tests if he is redirected toward the sociable'''
        client, user = auto_login_user()
        sociable     = SociableFactory(slug='test123', owner=user)
        LogMessageFactory(sociable=sociable, author=user)
        response     = client.get(self.url, {'search-code': sociable.slug})
        assert response.status_code == 302
        assert 'test123' in response.url


def test_update_unread_message_to_read(client):
    '''Given the click that the unread message is read,
    tests if the detailpage of the code is displayed with altering the is_read from the message'''
    sociable   = SociableFactory()
    logmessage = LogMessageFactory(sociable=sociable)
    url        = reverse('message-read', kwargs={'pk': logmessage.id})
    response   = client.get(url)
    logmessage = LogMessage.objects.get()

    assert response.status_code == 302
    assert logmessage.is_read
    assert sociable.slug in response.url


class TestgetSociablesForDashboard:
    '''Test the behavour of get_log_message_from_one_sociable'''
    def create_logmessage(self, number_of_messages: int, sociable: Sociable):
        '''Given the number of messages and the sociable,
        create that number of messages for the sociable'''
        for _ in range(number_of_messages):
            LogMessageFactory(sociable=sociable)

    def test_get_log_messages_from_one_sociable_with_no_messages(self, auto_login_user):
        '''Using the function create_logmessage and one sociable with no messages,
        tests if no sociables are retrieved'''
        _, owner = auto_login_user()
        SociableFactory(owner=owner)

        assert len(get_sociables_for_dashboard(owner)) == 0

    @pytest.mark.parametrize('number_of_messages', list(range(1, 3)))
    def test_get_log_messages_from_one_sociable(self, number_of_messages, auto_login_user):
        '''Using the function create_logmessage and one sociable,
        tests if one sociable is retrieved, no matter the number of messages'''
        _, owner      = auto_login_user()
        sociable_list = [SociableFactory(owner=owner)]

        self.create_logmessage(number_of_messages, sociable_list[0])

        assert len(get_sociables_for_dashboard(owner)) == 1

    def test_get_one_logmessage_from_one_sociable_not_from_user(self, auto_login_user):
        '''Given a user participating in a chat they did not initiate,
        test if it still returns the sociable'''
        _, user  = auto_login_user()
        sociable = SociableFactory()
        LogMessageFactory(sociable=sociable, author=user)

        assert len(get_sociables_for_dashboard(user)) == 1

    def test_get_two_logmessages_from_two_sociables(self, auto_login_user):
        '''Given two sociables with each a message,
        tests if it returns 2 sociables'''
        _, owner = auto_login_user()
        sociable_list_one = [SociableFactory(owner=owner), SociableFactory(owner=owner)]

        LogMessageFactory(sociable=sociable_list_one[0])
        LogMessageFactory(sociable=sociable_list_one[1])

        assert len(get_sociables_for_dashboard(owner)) == 2

    def test_get_one_logmessage_of_owner_of_sociable(self, auto_login_user):
        '''When a user is both the author and the owner of a logmessage,
        test if only one logmessage is retrieved'''
        _, owner = auto_login_user()
        sociable = SociableFactory(owner=owner)
        LogMessageFactory(sociable=sociable, author=owner)
        assert len(get_sociables_for_dashboard(owner)) == 1

    def test_one_logmessage_of_sociable_for_two_messages_of_author_and_owner(self, auto_login_user):
        '''Given a sociable with two messages,
        one from the owner of the sociable and one of a different user,
        test if only one sociable is retrieved'''
        _, owner = auto_login_user()
        author   = UserFactory()
        sociable = SociableFactory(owner=owner)
        LogMessageFactory(sociable=sociable, author=owner)
        LogMessageFactory(sociable=sociable, author=author)
        assert len(get_sociables_for_dashboard(owner)) == 1

    def test_get_empty_list_from_no_sociables(self, auto_login_user):
        '''Given no sociables,
        tests if it returns no logmessages'''
        _, owner = auto_login_user()
        assert len(get_sociables_for_dashboard(owner)) == 0

    def test_sorting_by_logmessages_descending_order(self, auto_login_user):
        '''Test if the sociables are returned in descending order by date created of logmessages'''
        _, user = auto_login_user()
        for i in range(0, 4):
            if i % 2 == 0:
                sociable = SociableFactory(slug=i, owner=user)
                LogMessageFactory(sociable=sociable)
            else:
                sociable = SociableFactory(slug=i)
                LogMessageFactory(sociable=sociable, author=user)

        sociable_list = list(get_sociables_for_dashboard(user))

        assert sociable_list[0].slug == '3'

    def test_sorting_after_adding_logmessage_at_same_sociable(self, auto_login_user):
        '''Test if the sociables are returned in descending order by date created of logmessages,
        when a logmessage is added to a previous sociable'''
        _, user = auto_login_user()
        for i in range(0, 4):
            if i % 2 == 0:
                sociable = SociableFactory(slug=i, owner=user)
                LogMessageFactory(sociable=sociable)
            else:
                sociable = SociableFactory(slug=i)
                LogMessageFactory(sociable=sociable, author=user)
        LogMessageFactory(sociable=Sociable.objects.get(slug='2'))

        sociable_list = get_sociables_for_dashboard(user)

        assert sociable_list[0].slug == '2'


class TestMultipleUnreadMessages:
    def test_only_unread_messages(self, client):
        '''Test when only unread messages,
        then the first unread message is shown'''
        sociable  = SociableFactory()
        for _ in range(5):
            LogMessageFactory(sociable=sociable)
        response = client.get(reverse('search-sociable'), {'search-code': sociable.slug})
        assert response.status_code == 200

    def test_3_of_5_unread_messages(self, client):
        '''Should then all names still be shown or only the 3 unread messages left?'''
        sociable  = SociableFactory()
        for _ in range(3):
            LogMessageFactory(sociable=sociable)
        for _ in range(2):
            LogMessageFactory(sociable=sociable, is_read=True)
        response = client.get(reverse('search-sociable'), {'search-code': sociable.slug})
        assert response.status_code == 200

    def test_1_unread_message(self, client):
        '''Test when only 1 unread message is there,
        then the page of multiple unread messages should not be shown'''
        sociable  = SociableFactory()
        LogMessageFactory(sociable=sociable)
        response = client.get(reverse('search-sociable'), {'search-code': sociable.slug})
        assert response.status_code == 200

    def test_no_unread_messages(self, client):
        '''Test when there are no unread messages,
        the detail page is shown'''
        sociable  = SociableFactory()
        for _ in range(3):
            LogMessageFactory(sociable=sociable, is_read=True)
        response = client.get(reverse('search-sociable'), {'search-code': sociable.slug})
        assert response.status_code == 302
        assert sociable.slug in response.url


def test_logmessage_str():
    '''Test the __str__ function of logmessage'''
    logmessage = LogMessageFactory(body='Hello, I am testing this body if it is truncated to 50.')
    assert str(logmessage) == 'Hello, I am testing this body if it is truncated t . . .'


def test_sociable_str():
    '''Test the __str__ function of sociable'''
    sociable = SociableFactory(slug='test123')
    assert str(sociable) == 'test123'
