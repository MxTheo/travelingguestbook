"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.utils import timezone
from django.contrib.auth.models import User
from streetactivity.models import StreetActivity, Word
from persona.models import Persona, Problem, Reaction

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    '''Mock for django.contrib.auth User'''
    class Meta:
        model = User
    username = factory.LazyFunction(fake.unique.name)
    email    = factory.LazyFunction(fake.unique.email)
    password = factory.LazyFunction(fake.unique.password)

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

class WordFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities Word'''
    class Meta:
        model = Word
    activity      = factory.SubFactory(StreetActivityFactory)
    word          = factory.LazyFunction(fake.word)
    date_created  = factory.LazyFunction(timezone.now)
    date_modified = factory.LazyFunction(timezone.now)
    user          = factory.SubFactory(UserFactory)

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
