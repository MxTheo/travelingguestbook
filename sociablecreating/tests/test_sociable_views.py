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
        assert 'test123' in response.url
        assert response.status_code == 302

    def test_search_with_slug_with_capital(self, client):
        '''Given a slug with a capital,
        tests if it returns the page with the sociable'''
        SociableFactory(slug='test123')
        response = client.get(self.url, {'search-code': 'Test123'})
        assert 'test123' in response.url
        assert response.status_code == 302

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
        assert 'sociablecreating/message.html' == response.templates[0].name

    def test_show_detailpage_when_message_is_read(self, client):
        '''Given a slug and a read message,
        tests if the detailpage is displayed'''
        sociable   = SociableFactory(slug='test123')
        LogMessageFactory(sociable=sociable, is_read=True)
        response   = client.get(self.url, {'search-code': sociable.slug})
        assert sociable.slug in response.url
        assert response.status_code == 302

    def test_show_sociable_when_user_is_owner(self,  auto_login_user):
        '''Given that the visitor is the owner, tests if the unread message is skipped and the sociable is shown'''
        client, user = auto_login_user()
        sociable     = SociableFactory(slug='test123', owner=user)
        LogMessageFactory(sociable=sociable)
        response     = client.get(self.url, {'search-code': sociable.slug})
        assert sociable.slug in response.url
        assert response.status_code == 302


def test_update_unread_message_to_read(client):
    '''Given the click that the unread message is read,
    tests if the detailpage of the code is displayed with altering the is_read from the message'''
    sociable = SociableFactory()
    logmessage = LogMessageFactory(sociable=sociable)
    url = reverse('message-read', kwargs={'pk': logmessage.id})
    response = client.get(url)
    logmessage = LogMessage.objects.get()

    assert response.status_code == 302
    assert logmessage.is_read
    assert sociable.slug in response.url


class TestGetLogmessageListFromSociableList:
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
        _, owner = auto_login_user()
        sociable_list = [SociableFactory(owner=owner)]

        self.create_logmessage(number_of_messages, sociable_list[0])

        assert len(get_sociables_for_dashboard(owner)) == 1


    def test_get_one_logmessage_from_one_sociable_that_does_not_belong_to_user(self, auto_login_user):
        '''Given a user participating in a chat they did not initiate, test if it still returns the sociable'''
        _, user = auto_login_user()
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

    def test_get_one_logmessage_of_sociable_with_two_messages_of_author_and_owner(self, auto_login_user):
        '''Given a sociable with two messages, one from the owner of the sociable and one of a different user,
        test if only one sociable is retrieved'''
        _, owner = auto_login_user()
        author = UserFactory()
        sociable = SociableFactory(owner=owner)
        LogMessageFactory(sociable=sociable, author=owner)
        LogMessageFactory(sociable=sociable, author=author)
        assert len(get_sociables_for_dashboard(owner)) == 1

    def test_get_empty_list_from_no_sociables(self, auto_login_user):
        '''Given no sociables,
        tests if it returns no logmessages'''
        _, owner = auto_login_user()
        assert len(get_sociables_for_dashboard(owner)) == 0


# def test_filter_out_double_sociables_for_list_logmessage(auto_login_user):
#     '''Given a user with multiple messages in one sociable,
#     tests if only one message is returned'''
#     _, author = auto_login_user()
#     sociable = SociableFactory()

#     list_logmessage = [LogMessageFactory(sociable=sociable, author=author) for _ in range(0,2)]

#     filtered_list = filter_out_double_sociables_for_list_logmessage(list_logmessage)

#     assert len(filtered_list) == 1


def test_logmessage_str():
    '''Test the __str__ function of logmessage'''
    logmessage = LogMessageFactory(body='Hello, I am testing this body if it is truncated to 50.')
    assert str(logmessage) == 'Hello, I am testing this body if it is truncated t . . .'


def test_sociable_str():
    '''Test the __str__ function of sociable'''
    sociable = SociableFactory(slug='test123')
    assert str(sociable) == 'test123'
