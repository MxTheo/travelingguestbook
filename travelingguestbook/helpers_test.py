from django.urls import reverse

def helper_test_page_rendering(client, name_of_page, arguments=None):
    url = reverse(name_of_page, args=arguments)
    response = client.get(url)
    assert response.status_code == 200