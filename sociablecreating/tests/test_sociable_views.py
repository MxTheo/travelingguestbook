from django.urls import reverse
import pytest
from travelingguestbook.factories import LogMessageFactory, SociableFactory
from sociablecreating.models import LogMessage, Sociable
from sociablecreating.views import get_logmessage_list_from_sociable_list

def test_message_sociable_relationship_set(client):
    '''Test if creating a log message results in a log message with a sociable relationship set'''
    sociable = SociableFactory()
    create_log_message_url = reverse('create-logmessage', args=[sociable.slug])

    client.post(create_log_message_url, data={'name': 'Tester', 'body': 'Hello'})

    logmessage_list = LogMessage.objects.all()
    assert logmessage_list[0].sociable == sociable

class TestFunGetLogmessageListFromSociableList:
    '''Test the behavour of get_log_message_from_one_sociable'''
    def create_logmessage(self, number_of_messages: int, sociable: Sociable):
        '''Given the number of messages and the sociable,
        create that number of messages for the sociable'''
        for _ in range(number_of_messages):
            LogMessageFactory(sociable=sociable)

    @pytest.mark.parametrize('number_of_messages', list(range(0,3)))
    def test_get_log_messages_from_one_sociable(self, number_of_messages):
        '''Using the function create_logmessage and one sociable,
        tests if all the messages are retrieved from the sociable for 0 till 3 log messages'''
        sociable_list_one = [SociableFactory()]

        self.create_logmessage( number_of_messages, sociable_list_one[0])

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
