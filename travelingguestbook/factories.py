"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.contrib.auth.models import User
from chatroomcreating.models import ChatRoom, ChatMessage

fake = Faker()

class RegistrationFactory(factory.django.DjangoModelFactory):
    """Mock for oogcontact Registration"""
    class Meta:
        model = 'oogcontact.Registration'
    name         = factory.LazyFunction(fake.name)
    email        = factory.LazyFunction(fake.email)
    date_created = factory.LazyFunction(fake.date_time_this_year)
    hasCanceled  = False

class UserFactory(factory.django.DjangoModelFactory):
    '''Mock for django.contrib.auth User'''
    class Meta:
        model = User
    username = factory.LazyFunction(fake.unique.name)
    email    = factory.LazyFunction(fake.unique.email)
    password = factory.LazyFunction(fake.unique.password)


class ChatRoomFactory(factory.django.DjangoModelFactory):
    '''Mock for chatroomcreating ChatRoom'''
    class Meta:
        model = ChatRoom
    slug   = factory.LazyFunction(fake.unique.postcode)
    secret_key = factory.LazyFunction(lambda: fake.sha256(raw_output=False))


class ChatMessageFactory(factory.django.DjangoModelFactory):
    '''Mock for chatroomcreation ChatMessage'''
    class Meta:
        model = ChatMessage
    body         = factory.LazyFunction(fake.text)
    chatroom     = factory.SubFactory(ChatRoomFactory)
    date_created = factory.LazyFunction(fake.date)
    nonce        = factory.LazyFunction(lambda: fake.sha256(raw_output=False))
