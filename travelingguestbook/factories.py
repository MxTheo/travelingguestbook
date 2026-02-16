"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.contrib.auth.models import User
from streetactivity.models import StreetActivity, Moment, Experience
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
    date_created  = factory.LazyFunction(fake.date)
    date_modified = factory.LazyFunction(fake.date)

class MomentFactory(factory.django.DjangoModelFactory):
    '''Mock for streetactivities Moment'''
    class Meta:
        model = Moment
    activity      = factory.SubFactory(StreetActivityFactory)
    report        = factory.LazyFunction(fake.text)
    confidence_level  = 0
    from_practitioner = False
    date_created  = factory.LazyFunction(fake.date)
    date_modified = factory.LazyFunction(fake.date)

class ExperienceFactory(factory.django.DjangoModelFactory):
    """
    Mock for streetactivity Experience
    """
    class Meta:
        model = Experience
        skip_postgeneration_save = True  # Avoid deprecation warning

    user = factory.SubFactory(UserFactory)
    date_created = factory.LazyFunction(fake.date)


class MomentWithExperienceFactory(MomentFactory):
    """Mock for streetactivities Moment with Experience"""
    experience = factory.SubFactory(ExperienceFactory)

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
