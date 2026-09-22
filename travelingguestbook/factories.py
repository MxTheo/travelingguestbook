"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

from gettogether.models import GetTogether
from persona.models import Persona, Problem, Reaction
from streetactivity.models import Reflection, StreetActivity

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    '''Mock for django.contrib.auth User'''
    class Meta:
        model = User
    username = factory.LazyFunction(fake.unique.name)
    email    = factory.LazyFunction(fake.unique.email)
    password = factory.LazyFunction(fake.unique.password)

class GetTogetherFactory(factory.django.DjangoModelFactory):
    """Mock for gettogether GetTogether"""
    class Meta:
        model = GetTogether
    location = factory.LazyFunction(fake.address)
    date     = factory.LazyFunction(timezone.now)
    user     = factory.SubFactory(UserFactory)

class StreetActivityFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities StreetActivity'''
    class Meta:
        model =  StreetActivity
    name          = factory.LazyFunction(fake.name)
    description   = factory.LazyFunction(fake.text)
    method        = 'invite'
    question      = factory.LazyFunction(fake.text)
    supplies      = factory.LazyFunction(fake.text)
    date_created  = factory.LazyFunction(timezone.now)
    date_modified = factory.LazyFunction(timezone.now)

class StreetActivityPhotoFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities StreetActivityPhoto'''
    class Meta:
        model =  'streetactivity.StreetActivityPhoto'
    activity      = factory.SubFactory(StreetActivityFactory)
    image         = factory.django.ImageField(color='blue')
    uploaded_at   = factory.LazyFunction(timezone.now)

class ReflectionFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities Reflection'''
    class Meta:
        model = Reflection
    activity        = factory.SubFactory(StreetActivityFactory)
    reflection      = factory.LazyFunction(fake.text)
    date_created    = factory.LazyFunction(timezone.now)
    date_modified   = factory.LazyFunction(timezone.now)
    external_id     = factory.Sequence(
        lambda n: f"at://did:plc:test/app.bsky.feed.post/{n}"
    )
    platform        = "Bluesky"
    author_username = factory.LazyFunction(fake.user_name)
    post_url        = factory.LazyFunction(fake.url)
    hashtags        = factory.LazyFunction(lambda: [fake.word()])

class PersonaFactory(factory.django.DjangoModelFactory):
    """Mock for persona Persona"""
    class Meta:
        model = Persona

    title = factory.Sequence(lambda n: f'Test Persona {n}')
    core_question = factory.Sequence(lambda n: f'Core question {n}?')
    description = factory.Faker('paragraph', nb_sentences=3)
    portrait = factory.LazyAttribute(lambda _: None)

class ProblemFactory(factory.django.DjangoModelFactory):
    """Mock for persona Problem"""
    class Meta:
        model = Problem

    persona = factory.SubFactory(PersonaFactory)
    description = factory.Sequence(lambda n: f'Problem text {n}')

class ReactionFactory(factory.django.DjangoModelFactory):
    """Mock for persona Reaction"""
    class Meta:
        model = Reaction

    persona = factory.SubFactory(PersonaFactory)
    description = factory.Sequence(lambda n: f'Reaction text {n}')