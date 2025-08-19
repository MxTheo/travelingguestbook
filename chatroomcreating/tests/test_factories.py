from travelingguestbook.factories import ChatMessageFactory, ChatRoomFactory, UserFactory


def test_chatroom_factory(chat_room_factory):
    """Tests if chatroom_factory is of type ChatRoomFactory"""
    assert chat_room_factory is ChatRoomFactory


def test_chat_message_factory(chat_message_factory):
    """Tests if chat_message_factory is of type ChatMessageFactory"""
    assert chat_message_factory is ChatMessageFactory


def test_user_factory(user_factory):
    """Tests if user_factory is of type UserFactory"""
    assert user_factory is UserFactory
