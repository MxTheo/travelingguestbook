import base64
from django.urls import reverse
from travelingguestbook.factories import ChatMessageFactory, ChatRoomFactory
from travelingguestbook.helpers_test import create_chatmessage
from chatroomcreating.models import ChatMessage, ChatRoom


def test_create_chatroom_view(client):
    '''Test the create_chatroom view to ensure it creates a ChatRoom object and redirects correctly.'''
    url = reverse('create-chatroom')

    response = client.post(url)

    assert response.status_code == 302

    assert ChatRoom.objects.exists()

    chatroom = ChatRoom.objects.first()
    assert len(chatroom.slug) == 9
    expected_url = reverse('chatroom', args=[chatroom.slug])
    assert response.url == expected_url

def test_chatroom_generates_secret_key(client):
    """Test if the chatroom generates a secret key upon creation."""
    url = reverse('create-chatroom')
    client.post(url)
    chatroom = ChatRoom.objects.first()
    assert chatroom.secret_key is not None
    assert isinstance(chatroom.secret_key, str)
    decoded_key = base64.b64decode(chatroom.secret_key)
    assert len(decoded_key) == 32  # Check if the key is 32 bytes

def test_chatroom_secret_key_is_unique(client):
    """Test if the secret key is unique for each chatroom."""
    url = reverse('create-chatroom')
    client.post(url)
    chatroom = ChatRoom.objects.first()

    client.post(url)
    chatroom2 = ChatRoom.objects.first()
    assert chatroom.secret_key != chatroom2.secret_key

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
        chatroom    = ChatRoomFactory()
        chatmessage = create_chatmessage(client, chatroom)
        assert chatmessage.chatroom == chatroom

    def test_create_chatmessage_by_anonymous(self, client):
        """Logged in as an anonymous user,
        test if the user can create a chatmessage"""
        chatroom = ChatRoomFactory()
        chatmessage = create_chatmessage(client, chatroom)
        assert chatmessage.body == "create_chatmessage"
        assert chatmessage.chatroom == chatroom
        assert chatmessage.nonce == "dGVzdG5vbmNl"


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
    assert absolute_url == "/c/" + str(chatroom.slug)
    response     = client.get(absolute_url)
    assert response.status_code == 200
