from django.urls import reverse
import pytest
from travelingguestbook.factories import LogMessageFactory, SociableFactory
from sociablecreating.models import Sociable, LogMessage
from sociablecreating.views import get_logmessage_list_from_sociable_list


class TestSearchSociable:
    '''Test the behaviour of search_sociable'''
    url = reverse('search-sociable')

    def setup_method(self):
        '''For every test, a sociable with slug test123 is used
        and url is search-sociable'''
        SociableFactory(slug='test123')

    def test_search_with_correct_slug(self, client):
        '''Given correct slug,
        tests if it returns the page with the sociable'''
        response = client.get(self.url, {'search-code': 'test123'})
        assert 'test123' in response.url
        assert response.status_code == 302

    def test_search_with_slug_with_capital(self, client):
        '''Given a slug with a capital,
        tests if it returns the page with the sociable'''
        response = client.get(self.url, {'search-code': 'Test123'})
        assert 'test123' in response.url
        assert response.status_code == 302

    def test_search_with_incorrect_slug(self, client):
        '''Given incorrect slug,
        tests if it returns Not Found'''
        response = client.get(self.url, {'search-code': 'test456'})
        assert b'niet gevonden' in response.content
        assert response.status_code == 200

    def test_search_with_no_slug(self, client):
        '''Given empty slug,
        tests if it returns Not Found

        A user cannot enter None.
        Even when the user presses enter, the search-code will not be none, but an empty string.
        Therefore, input None will not work and is not tested'''
        response = client.get(self.url, {'search-code': ''})
        assert b'niet gevonden' in response.content
        assert response.status_code == 200

    def test_show_unread_message(self, client):
        '''Given a slug and an unread message,
        tests if the unread message is displayed'''
        sociable   = Sociable.objects.get(slug='test123')
        LogMessageFactory(sociable=sociable)
        response   = client.get(self.url, {'search-code': sociable.slug})
        assert response.status_code == 200
        assert 'sociablecreating/message.html' == response.templates[0].name

    def test_show_detailpage_when_message_is_read(self, client):
        '''Given a slug and a read message,
        tests if the detailpage is displayed'''
        sociable   = Sociable.objects.get(slug='test123')
        LogMessageFactory(sociable=sociable, is_read=True)
        response   = client.get(self.url, {'search-code': sociable.slug})
        assert sociable.slug in response.url
        assert response.status_code == 302


class TestGetLogmessageListFromSociableList:
    '''Test the behavour of get_log_message_from_one_sociable'''
    def create_logmessage(self, number_of_messages: int, sociable: Sociable):
        '''Given the number of messages and the sociable,
        create that number of messages for the sociable'''
        for _ in range(number_of_messages):
            LogMessageFactory(sociable=sociable)

    @pytest.mark.parametrize('number_of_messages', list(range(0, 3)))
    def test_get_log_messages_from_one_sociable(self, number_of_messages):
        '''Using the function create_logmessage and one sociable,
        tests if all the messages are retrieved from the sociable for 0 till 3 log messages'''
        sociable_list_one = [SociableFactory()]

        self.create_logmessage(number_of_messages, sociable_list_one[0])

        assert len(get_logmessage_list_from_sociable_list(sociable_list_one)) == number_of_messages

    def test_get_list_of_two_logmessages_from_two_sociables(self):
        '''Given two sociables with each a message,
        tests if it returns 2 messages'''
        sociable_list_one = [SociableFactory(), SociableFactory()]

        LogMessageFactory(sociable=sociable_list_one[0])
        LogMessageFactory(sociable=sociable_list_one[1])

        assert len(get_logmessage_list_from_sociable_list(sociable_list_one)) == 2

    def test_get_empty_list_from_no_sociables(self):
        '''Given no sociables,
        tests if it returns no logmessages'''
        assert len(get_logmessage_list_from_sociable_list([])) == 0


def test_logmessage_str():
    '''Test the __str__ function of logmessage'''
    logmessage = LogMessageFactory(body='Hello, I am testing this body if it is truncated to 50.')
    assert str(logmessage) == 'Hello, I am testing this body if it is truncated t . . .'


def test_sociable_str():
    '''Test the __str__ function of sociable'''
    sociable = SociableFactory(slug='test123')
    assert str(sociable) == 'test123'
