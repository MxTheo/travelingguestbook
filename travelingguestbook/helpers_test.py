from django.urls import reverse


def helper_test_page_rendering(client, name_of_page, keyword_arguments=None):
    '''Given, the client, a name of the page and optional keyword_arguments,
    tests if the client responds with OK, success'''
    url = reverse(name_of_page, kwargs=keyword_arguments)
    response = client.get(url)
    assert response.status_code == 200
