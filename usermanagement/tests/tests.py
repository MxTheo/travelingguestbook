'''Followed the tutorial: https://djangostars.com/blog/django-pytest-testing/'''
from django.urls import reverse
from travelingguestbook.helpers_test import create_user_and_profile_with_custom_description, helper_test_page_rendering
from usermanagement.models import Profile
from usermanagement.views import clear_custom_description_for_code


def test_view(client):
    '''Given the homepage,
    tests it the homepage is reached'''
    helper_test_page_rendering(client, 'home')


def test_auth_view(auto_login_user):
    '''Logged in,
    tests if the user reaches dashboard'''
    client, _ = auto_login_user()
    helper_test_page_rendering(client, 'dashboard')


def test_clear_custom_description(auto_login_user):
    '''When user resets custom description,
    test if the default description is used again'''
    cust_descr = 'This should be changed and not be used as description'
    client, user = create_user_and_profile_with_custom_description(auto_login_user, cust_descr)
    clear_custom_description_for_code(user)
    profile = Profile.objects.get(user=user)
    assert profile.custom_description_for_code == ''
    response = client.get(reverse('create-sociable'))
    assert 'Ik heb een bericht voor je achter gelaten. Leuk als je reageert, hoeft niet. Vertel iets over jouw ervaringen van ons gesprek. Nu is het aan jou om deze gespreksketen voor te zetten.' in str(response.content)

def test_reset_custom_description(auto_login_user):
    '''When user clicks reset omschrijving,
    test if the page is redirected to the sociable form'''
    cust_descr = 'This should be changed and not be used as description'
    client, _ = create_user_and_profile_with_custom_description(auto_login_user, cust_descr)
    response = client.get(reverse('resetdescription'))
    assert response.status_code == 302
