import base64

import nacl
from chatroomcreating.models import ChatMessage, ChatRoom
from travelingguestbook.factories import ChatMessageFactory, ChatRoomFactory

def test_home_view(client):
    """Test the home view to ensure it renders the homepage correctly."""
    response = client.get('/uitwisseling')
    assert response.status_code == 200

def test_chatmessage_str():
    '''Test the __str__ function of chatmessage'''
    chatmessage = ChatMessageFactory(body='Hello, I am testing this body if it is truncated to 50.')
    assert str(chatmessage) == 'Hello, I am testing this body if it is truncated t . . .'


def test_chatroom_str():
    '''Test the __str__ function of chatroom'''
    chatroom = ChatRoomFactory(slug='test123')
    assert str(chatroom) == 'test123'

def test_get_decrypt_key():
    '''Test the get_decrypt_key method of ChatMessage'''
    raw_key = b'0123456789abcdef0123456789abcdef'
    key_b64 = base64.b64encode(raw_key).decode('utf-8')
    chatroom = ChatRoom.objects.create(secret_key=key_b64)

    chatmessage = ChatMessage.objects.create(chatroom=chatroom, body="test")

    decoded_key = chatmessage.get_decrypt_key()

    assert isinstance(decoded_key, bytes)
    assert decoded_key == raw_key

def test_decrypted_body():
    '''Test the decrypted_body property of ChatMessage'''
    original_message = "Hello secret world!"

    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key_b64 = base64.b64encode(key).decode('utf-8')

    box = nacl.secret.SecretBox(key)

    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    encrypted = box.encrypt(original_message.encode('utf-8'), nonce)

    ciphertext = encrypted.ciphertext

    nonce_b64 = base64.b64encode(nonce).decode('utf-8')
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')

    chatroom = ChatRoom.objects.create(secret_key=key_b64)
    chatmessage = ChatMessage.objects.create(
        chatroom=chatroom,
        body=ciphertext_b64,
        nonce=nonce_b64
    )

    assert chatmessage.decrypted_body == original_message

def test_decrypted_body_with_decryption_error():
    '''Test the decrypted_body property handles decryption errors gracefully'''
    chatroom = ChatRoom.objects.create(secret_key="not_base64!")

    chatmessage = ChatMessage.objects.create(
        chatroom=chatroom, 
        body="invalid_base64_body===", 
        nonce="also_invalid_base64==="
    )

    decrypted = chatmessage.decrypted_body
    assert decrypted.startswith("[Fout bij decryptie]")
