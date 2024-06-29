from contact.views import get_mailto_url
from travelingguestbook.factories import UserFactory

class TestGetMailToUrl:
    '''Tests for the function get_mailto_url'''
    def setup_method(self):
        '''For every test, an admin account has to be created'''
        UserFactory(username='admin', email='test@info.com')

    def test_get_mailto_url(self):
        '''Test if mailto redirects user to the mailto url with admin mail address'''
        mailto_url = get_mailto_url()
        assert mailto_url == 'mailto:test@info.com'
