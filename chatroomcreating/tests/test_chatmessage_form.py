from django.urls import reverse
from travelingguestbook.factories import ChatRoomFactory

def test_form_template_renders_and_contains_textarea(client):
    '''Test that the chat message form renders correctly and contains a textarea with the correct id.'''
    chatroom = ChatRoomFactory()
    url = reverse('create-chatmessage', kwargs={'slug': chatroom.slug})
    response = client.get(url)

    assert response.status_code == 200
    assert 'chatroomcreating/chatmessage_form.html' in [t.name for t in response.templates]

    # Controleer of textarea met id 'id_body' in de response HTML zit
    assert '<textarea' in response.content.decode()
    assert 'id="id_body"' in response.content.decode()
