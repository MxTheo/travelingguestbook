from django.urls import reverse
from chatroomcreating.models import ChatMessage
from travelingguestbook.factories import ChatRoomFactory


def helper_test_page_rendering(client, name_of_page, keyword_arguments=None):
    '''Given, the client, a name of the page and optional keyword_arguments,
    tests if the client responds with OK, success'''
    url = reverse(name_of_page, kwargs=keyword_arguments)
    response = client.get(url)
    assert response.status_code == 200


def create_chatmessage(client, chatroom=None, data=None):
    '''Given the client and optional data for the chatroom,
    creates a chatmessage using the CreateView for unittesting purposes'''
    if chatroom is None:
        chatroom = ChatRoomFactory()
    if data is None:
        data = {'name': 'create_chatmessage', 'body': 'create_chatmessage',"nonce": "dGVzdG5vbmNl"}
    url_create = reverse('create-chatmessage', args=[chatroom.slug])
    client.post(url_create, data=data)
    return ChatMessage.objects.filter(chatroom=chatroom)[0]
