"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.contrib.auth.models import User
from streetactivity.models import StreetActivity
from chatroomcreating.models import ChatRoom, ChatMessage
from persona.models import Persona, Problem, Reaction

fake = Faker()

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
    slug       = factory.LazyFunction(fake.unique.postcode)
    secret_key = factory.LazyFunction(lambda: fake.sha256(raw_output=False))


class ChatMessageFactory(factory.django.DjangoModelFactory):
    '''Mock for chatroomcreation ChatMessage'''
    class Meta:
        model = ChatMessage
    body         = factory.LazyFunction(fake.text)
    chatroom     = factory.SubFactory(ChatRoomFactory)
    date_created = factory.LazyFunction(fake.date)
    nonce        = factory.LazyFunction(lambda: fake.sha256(raw_output=False))

class StreetActivityFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities StreetActivity'''
    class Meta:
        model =  StreetActivity
    name          = factory.LazyFunction(fake.name)
    description   = factory.LazyFunction(fake.text)
    method        = 'invite'
    question      = factory.LazyFunction(fake.text)
    supplies      = factory.LazyFunction(fake.text)
    difficulty    = 3
    chance        = 3
    needHelp      = False
    date_created  = factory.LazyFunction(fake.date)
    date_modified = factory.LazyFunction(fake.date)

class PersonaFactory(factory.django.DjangoModelFactory):
    """Mock for persona Persona"""
    class Meta:
        model = Persona

    title = factory.Sequence(lambda n: f'Test Persona {n}')
    core_question = factory.Sequence(lambda n: f'Core question {n}?')
    description = factory.Faker('paragraph', nb_sentences=3)

class ProblemFactory(factory.django.DjangoModelFactory):
    """Mock for persona Problem"""
    class Meta:
        model = Problem

    persona = factory.SubFactory(PersonaFactory)
    text = factory.Sequence(lambda n: f'Problem text {n}')

class ReactionFactory(factory.django.DjangoModelFactory):
    """Mock for persona Reaction"""
    class Meta:
        model = Reaction

    persona = factory.SubFactory(PersonaFactory)
    text = factory.Sequence(lambda n: f'Reaction text {n}')
