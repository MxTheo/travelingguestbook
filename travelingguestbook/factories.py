"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.contrib.auth.models import User
from streetactivity.models import StreetActivity, ExternalReference, SWOTElement
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

class ExternalReferenceFactory(factory.django.DjangoModelFactory):
    """Mock for streetactivities ExternalReference"""
    class Meta:
        model = ExternalReference

    activity = factory.SubFactory('travelingguestbook.factories.StreetActivityFactory')
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=3)

    url = factory.Faker('url')
    reference_type = factory.Faker('random_element', elements=[
        'persoonlijke ervaring',
        'boek', 
        'onderzoek',
        'theorie',
        'inspiratie',
        'video',
        'blog',
        'academisch artikel',
        ''
    ])
    submitted_by = factory.Faker('name')

class BookReferenceFactory(ExternalReferenceFactory):
    """Factory specific for book references (without URL)"""
    reference_type = "boek"
    url = ""
    title = factory.Faker('sentence', nb_words=3)
    description = factory.LazyAttribute(lambda o: f"Boek: {o.title}")

class PersonalExperienceFactory(ExternalReferenceFactory):
    """Factory specific for personal experiences"""
    reference_type = "persoonlijke ervaring"
    submitted_by = factory.Faker('name')
    title = factory.LazyAttribute(lambda o: f"Mijn ervaring met {o.activity.name}")
    description = factory.Faker('paragraph', nb_sentences=4)

class ResearchReferenceFactory(ExternalReferenceFactory):
    """Factory specific for research references"""
    reference_type = "onderzoek"
    title = factory.LazyAttribute(lambda o: f"Onderzoek naar {o.activity.name}")
    description = factory.LazyAttribute(lambda o: f"Academisch onderzoek gerelateerd aan {o.activity.name}")

class SWOTElementFactory(factory.django.DjangoModelFactory):
    """Factory for SWOTElement model"""
    
    class Meta:
        model = SWOTElement
    
    street_activity = factory.SubFactory(StreetActivityFactory)
    element_type = factory.LazyFunction(
        lambda: fake.random_element(elements=('S', 'W', 'O', 'T'))
    )
    formulation = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    recognition_count = 0
    alternative_formulation = None
    votes_current = 0
    votes_alternative = 0
    needs_voting = False