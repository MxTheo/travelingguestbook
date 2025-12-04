"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.contrib.auth.models import User
from streetactivity.models import StreetActivity, Experience
from persona.models import Persona, Problem, Reaction
from streetpartner.models import PartnershipRequest, StreetPartnership

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
    date_created  = factory.LazyFunction(fake.date)
    date_modified = factory.LazyFunction(fake.date)

class ExperienceFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities Experience'''
    class Meta:
        model = Experience
    activity      = factory.SubFactory(StreetActivityFactory)
    report        = factory.LazyFunction(fake.text)
    confidence_level          = 'pioneer'
    from_practitioner = False
    date_created  = factory.LazyFunction(fake.date)
    date_modified = factory.LazyFunction(fake.date)
    keywords      = factory.LazyFunction(lambda: ', '.join([fake.word() for _ in range(3)]))

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

class PartnershipRequestFactory(factory.django.DjangoModelFactory):
    """Mock for request of a partnership"""
    class Meta:
        model = PartnershipRequest
    from_user = factory.SubFactory(UserFactory)
    to_user = factory.SubFactory(UserFactory)
    message = factory.LazyFunction(fake.text)
    status = 'pending'

class StreetPartnershipFactory(factory.django.DjangoModelFactory):
    """Mock for Streetpartnership"""
    class Meta:
        model = StreetPartnership
    user1 = factory.SubFactory(UserFactory)
    user2 = factory.SubFactory(UserFactory)
    partnership_request = factory.SubFactory(PartnershipRequestFactory)