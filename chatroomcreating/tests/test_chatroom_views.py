import base64

import nacl
from chatroomcreating.models import ChatMessage, ChatRoom
from travelingguestbook.factories import ChatMessageFactory, ChatRoomFactory

def test_home_view(client):
    """Test the home view to ensure it renders the homepage correctly."""
    response = client.get('/chat')
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
    raw_key = b'0123456789abcdef0123456789abcdef'  # 32 bytes sleutel
    key_b64 = base64.b64encode(raw_key).decode('utf-8')
    chatroom = ChatRoom.objects.create(secret_key=key_b64)

    chatmessage = ChatMessage.objects.create(chatroom=chatroom, body="test")

    decoded_key = chatmessage.get_decrypt_key()

    assert isinstance(decoded_key, bytes)
    assert decoded_key == raw_key

def test_decrypted_body():
    '''Test the decrypted_body property of ChatMessage'''
    # Original plaintext message
    original_message = "Hello secret world!"

    # Generate a 32-byte random key and base64 encode it
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key_b64 = base64.b64encode(key).decode('utf-8')

    # Create the SecretBox with this key
    box = nacl.secret.SecretBox(key)

    # Generate nonce
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    # Encrypt the message
    encrypted = box.encrypt(original_message.encode('utf-8'), nonce)

    # Extract ciphertext without nonce (PyNaCl's encrypt prepends nonce, so slice)
    ciphertext = encrypted.ciphertext

    # Base64 encode nonce and ciphertext for storage like your model
    nonce_b64 = base64.b64encode(nonce).decode('utf-8')
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')

    # Create ChatRoom and ChatMessage
    chatroom = ChatRoom.objects.create(secret_key=key_b64)
    chatmessage = ChatMessage.objects.create(
        chatroom=chatroom,
        body=ciphertext_b64,
        nonce=nonce_b64
    )

    # Test the decrypted_body property returns original plaintext
    assert chatmessage.decrypted_body == original_message

def test_decrypted_body_with_decryption_error():
    '''Test the decrypted_body property handles decryption errors gracefully'''
    # Create a ChatRoom with an invalid base64 key (to trigger decode error later)
    chatroom = ChatRoom.objects.create(secret_key="not_base64!")

    # Create a ChatMessage with invalid base64 for body and nonce to trigger error
    chatmessage = ChatMessage.objects.create(
        chatroom=chatroom, 
        body="invalid_base64_body===", 
        nonce="also_invalid_base64==="
    )

    # Access decrypted_body, should catch an exception and return error string
    decrypted = chatmessage.decrypted_body
    assert decrypted.startswith("[Fout bij decryptie]")
