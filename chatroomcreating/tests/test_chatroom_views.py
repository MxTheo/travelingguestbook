from travelingguestbook.factories import ChatMessageFactory, ChatRoomFactory


def test_chatmessage_str():
    '''Test the __str__ function of chatmessage'''
    chatmessage = ChatMessageFactory(body='Hello, I am testing this body if it is truncated to 50.')
    assert str(chatmessage) == 'Hello, I am testing this body if it is truncated t . . .'


def test_chatroom_str():
    '''Test the __str__ function of chatroom'''
    chatroom = ChatRoomFactory(slug='test123')
    assert str(chatroom) == 'test123'
