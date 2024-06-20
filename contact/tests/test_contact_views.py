from contact.views import get_mailto_url
import pytest

from travelingguestbook.factories import UserFactory

class TestGetMailToUrl:
    def setup_method(self, test_method):
        UserFactory(username='admin', email='test@info.com')

    def test_get_mailto_url(self):
        '''Test if mailto redirects user to the mailto url with admin mail address'''
        
        mailto_url = get_mailto_url()
        assert mailto_url == 'mailto:test@info.com'