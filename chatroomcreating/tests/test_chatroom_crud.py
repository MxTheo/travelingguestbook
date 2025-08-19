from datetime import date
from django.urls import reverse
from travelingguestbook.factories import ChatMessageFactory, ChatRoomFactory
from travelingguestbook.helpers_test import create_chatmessage
from chatroomcreating.models import ChatMessage, ChatRoom


def test_create_chatroom_view(client):
    '''Test the create_chatroom view to ensure it creates a ChatRoom object and redirects correctly.'''
    url = reverse('create-chatroom')  # pas aan naar jouw url name
    
    # Doe een POST request naar de view
    response = client.post(url)
    
    # Check dat het antwoord een redirect is (statuscode 302)
    assert response.status_code == 302
    
    # Check dat er een ChatRoom object is aangemaakt
    assert ChatRoom.objects.exists()
    
    # Check dat de redirect locatie de detail url is van het gemaakte object
    chatroom = ChatRoom.objects.first()
    assert len(chatroom.slug) == 21  # Controleer of de slug correct is aangemaakt
    expected_url = reverse('chatroom', args=[chatroom.slug])
    assert response.url == expected_url

class TestDeleteChatRoom:
    """Test user permissions for deleting a chatroom"""

    def test_delete_chatroom_without_authentication(self, client):
        """Not logged in,
        tests if the anonymous user is able to delete the chatroom"""
        chatroom = ChatRoomFactory()

        delete_chatroom_url = reverse("delete-chatroom", args=[chatroom.slug])
        client.delete(delete_chatroom_url)

        assert ChatRoom.objects.count() == 0


class TestDeleteChatMessage:
    """Test user permissions to delete chatmessage"""

    def test_delete_chatmessage_without_authentication(self, client):
        """Not logged in,
        tests if the anonymous user is able to delete the chatmessage"""
        chatroom       = ChatRoomFactory()
        chatmessage = ChatMessageFactory(chatroom=chatroom)

        delete_chatmessage_url = reverse("delete-chatmessage", args=[chatmessage.id])
        client.delete(delete_chatmessage_url)

        assert ChatMessage.objects.count() == 0


class TestCreateChatMessage:
    """Tests for creating chatmessage"""

    def test_message_chatroom_relationship_set(self, client):
        """Given a chatroom and creating a chatmessage,
        tests if the chatroom relationship is set"""
        chatroom       = ChatRoomFactory()
        chatmessage = create_chatmessage(client, chatroom)
        assert chatmessage.chatroom == chatroom

    def test_if_name_is_not_changed_with_anonymous_user(self, client):
        """Not logged in, tests if the name is not altered"""
        chatmessage = create_chatmessage(
            client, data={"name": "test-name", "body": "test-body"}
        )
        assert chatmessage.name == "test-name"

class TestUpdateChatMessage:
    """Test user permissions for updating chatmessage"""

    def test_update_chatmessage_by_anonymous(self, client):
        """Logged in as an anonymous user,
        test if the user cannot update the chatmessage"""
        chatroom   = ChatRoomFactory()
        chatmessage = ChatMessageFactory(chatroom=chatroom)
        chatmessage_changed = self.update_chatmessage(client, chatmessage, "Hello")
        assert chatmessage_changed.body == "Hello"
        assert chatmessage_changed.date_changed.date() == date.today()

    def update_chatmessage(self, client, chatmessage, message_body):
        """Given the chatmessage and the textbody,
        change the message_body"""
        url_update = reverse("update-chatmessage", args=[chatmessage.id])
        client.post(url_update, data={"body": message_body, "name": chatmessage.name})
        return ChatMessage.objects.get(id=chatmessage.id)


class TestDetailChatRoom:
    """Tests for DetailView of ChatRoom"""

    def test_detail_page(self, client):
        """Test if the detailpage is reached"""
        chatroom = ChatRoomFactory(slug="test")
        url      = reverse("chatroom", args=[chatroom.slug])
        response = client.get(url)

        assert response.status_code == 200


def test_chatroom_absolute_url_with_200(client):
    """Tests if the slug is used as absolute url of the chatroom"""
    chatroom     = ChatRoomFactory()
    absolute_url = chatroom.get_absolute_url()
    assert absolute_url == "/c/" + str(chatroom.slug)+'/'
    response     = client.get(absolute_url)
    assert response.status_code == 200
