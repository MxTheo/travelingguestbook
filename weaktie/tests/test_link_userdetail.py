from django.urls import reverse

from travelingguestbook.factories import UserFactory


def test_display_domain_of_link(client):
    """Test that the domain of a link is displayed correctly in the UserDetail view."""
    user = UserFactory()
    link = user.links.create(url="https://www.example.com/path/to/resource")

    url = reverse("user", kwargs={"username": user.username})
    response = client.get(url)

    assert response.status_code == 200
    assert link.domain in response.content.decode()

def test_display_handle_of_link(client):
    """Test that the handle of a social media profile, the last part of the url, is displayed correctly in the UserDetail view."""
    user = UserFactory()
    link = user.links.create(url="https://www.example.com/path/to/resource")

    url = reverse("user", kwargs={"username": user.username})
    response = client.get(url)

    assert response.status_code == 200
    assert link.handle in response.content.decode()

def test_display_handle_of_link_without_path(client):
    """Test that the handle of a social media profile, the last part of the url, is displayed correctly in the UserDetail view."""
    user = UserFactory()
    link = user.links.create(url="https://www.example.com")

    url = reverse("user", kwargs={"username": user.username})
    response = client.get(url)

    assert response.status_code == 200
    assert link.handle in response.content.decode()

def test_links_in_context(client):
    """Test that links are correctly added to the context in UserDetail view."""
    user = UserFactory()
    link1 = user.links.create(url="https://www.example.com/path/to/resource")
    link2 = user.links.create(url="https://www.anotherexample.com/another/path")

    url = reverse("user", kwargs={"username": user.username})
    response = client.get(url)

    assert response.status_code == 200
    assert link1 in list(response.context["links"])
    assert link2 in list(response.context["links"])