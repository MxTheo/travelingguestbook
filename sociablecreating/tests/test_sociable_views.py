from django.urls import reverse
from travelingguestbook.factories import LogMessageFactory, SociableFactory
from sociablecreating.models import LogMessage, Sociable
from sociablecreating.views import get_logmessage_list_from_sociable_list
import pytest

def test_message_sociable_relationship_set(client):
    '''Test if creating a log message results in a log message with a sociable relationship set'''

    sociable = SociableFactory()
    create_log_message_url = reverse('create-logmessage', args=[sociable.slug])

    client.post(create_log_message_url, data={'name': 'Tester', 'body': 'Hello'})

    logmessage_list = LogMessage.objects.all()
    assert logmessage_list[0].sociable == sociable

class TestFunGetLogmessageListFromSociableList:
    def create_logmessage(self, number_of_messages: int, sociable: Sociable):
        for _ in range(number_of_messages):
            LogMessageFactory(sociable=sociable)
    
    @pytest.mark.parametrize('number_of_messages', list(range(0,3)))
    def test_get_log_messages_from_one_sociable(self, number_of_messages):
        sociable_list_one = [SociableFactory()]

        self.create_logmessage( number_of_messages, sociable_list_one[0])

        assert len(get_logmessage_list_from_sociable_list(sociable_list_one)) == number_of_messages

    def test_get_list_of_two_logmessages_from_two_sociables(self):
        sociable_list_one = [SociableFactory(), SociableFactory()]

        LogMessageFactory(sociable=sociable_list_one[0]) 
        LogMessageFactory(sociable=sociable_list_one[1])
        
        assert len(get_logmessage_list_from_sociable_list(sociable_list_one)) == 2

    def test_get_empty_list_from_no_sociables(self):
        assert len(get_logmessage_list_from_sociable_list([])) == 0
