"""Module that has the factories configured for the different modules,
to be able to mock the objects in tests"""

import factory
from faker import Faker
from django.contrib.auth.models import User
from sociablecreating.models import Sociable, LogMessage

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    '''Mock for django.contrib.auth User'''
    class Meta:
        model = User
    username = factory.LazyFunction(fake.unique.name)
    email    = factory.LazyFunction(fake.unique.email)
    password = factory.LazyFunction(fake.unique.password)


class SociableFactory(factory.django.DjangoModelFactory):
    '''Mock for sociablecreating Sociable'''
    class Meta:
        model = Sociable
    slug  = factory.LazyFunction(fake.unique.postcode)
    owner = factory.SubFactory(UserFactory)
    description = factory.LazyFunction(fake.text)


class LogMessageFactory(factory.django.DjangoModelFactory):
    '''Mock for sociablecreation LogMessage'''
    class Meta:
        model = LogMessage
    body     = factory.LazyFunction(fake.text)
    name     = factory.LazyFunction(fake.name)
    sociable = factory.SubFactory(SociableFactory)
    date_created = factory.LazyFunction(fake.date)
    date_modified = factory.LazyFunction(fake.date)
