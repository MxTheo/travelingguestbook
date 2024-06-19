from contact.views import get_mailto_url
import pytest

def test_mailto():
    '''Test if mailto redirects user to the mailto url with admin mail address'''
    mailto_url = get_mailto_url()
    assert mailto_url == 'mailto:theoschutte@me.com'