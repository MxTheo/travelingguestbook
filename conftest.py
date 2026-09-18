from __future__ import annotations

import sys
import tempfile
import uuid

import pytest
from pytest_factoryboy import register

from travelingguestbook import factories
from usermanagement import reserved as reserved_module

register(factories.StreetActivityFactory)
register(factories.ReflectionFactory)
register(factories.PersonaFactory)
register(factories.ProblemFactory)
register(factories.ReactionFactory)

#: Source of the temporary URLconf used by :func:`temp_urlconf`.
#:
#: The patterns are deliberately self-contained: they include only dummy
#: views defined inline, so the test does not depend on the project's real
#: URLconf, admin, or any other app. This keeps the reserved-segment
#: discovery test isolated and fast.
_TEMP_URLCONF_SOURCE = """
from django.http import HttpResponse
from django.urls import include, path


def _view(request):
    return HttpResponse("ok")


urlpatterns = [
    path("admin/", _view),
    path("contact/", _view),
    path("overons/", _view),
    path("accounts/", include("usermanagement.profile_urls")),  # → URLResolver
    path("<username:username>/", _view),
]
"""

@pytest.fixture()
def temporary_media_root(settings):
    """Use temporary directory for media files during tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        yield temp_dir

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    '''This function saves us from typing @pytest.mark.django_db before every test function'''

@pytest.fixture(name='create_user')
def create_user(django_user_model):
    '''Custom user fixture according to https://djangostars.com/blog/django-pytest-testing/,
    to create a test user'''
    def make_user(**kwargs):
        kwargs['password'] = 'strong-test-pass'
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
            kwargs['email'] = 'info@test.com'
        return django_user_model.objects.create_user(**kwargs)
    return make_user

@pytest.fixture
def auto_login_user(client, create_user):
    '''Custom login fixtur according to https://djangostars.com/blog/django-pytest-testing/,
    to log in for test'''
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.username, password='strong-test-pass')
        return client, user
    return make_auto_login

@pytest.fixture
def temp_urlconf(settings, tmp_path):
    """Create a temporary URLconf module and install it via settings.

    Writes a small, self-contained URLconf to a temporary directory, adds
    that directory to ``sys.path``, and points ``settings.ROOT_URLCONF``
    at it. The reserved-segments cache is cleared before and after the
    test so that both the temporary and the real URLconf are re-evaluated
    on demand.

    Args:
        settings: The pytest-django settings fixture.
        tmp_path: The pytest ``tmp_path`` fixture.

    Yields:
        The module name of the temporary URLconf (``"temp_urls"``).
    """
    module_file = tmp_path / "temp_urls.py"
    module_file.write_text(_TEMP_URLCONF_SOURCE)

    sys.path.insert(0, str(tmp_path))
    try:
        settings.ROOT_URLCONF = "temp_urls"
        reserved_module.reserved_segments.cache_clear()
        yield "temp_urls"
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("temp_urls", None)
        reserved_module.reserved_segments.cache_clear()


@pytest.fixture(autouse=True)
def clear_reserved_cache():
    """Clear the reserved-segments cache around every test.

    Ensures each test starts with a fresh cache regardless of whether it
    uses the ``temp_urlconf`` fixture.

    Yields:
        None
    """
    reserved_module.reserved_segments.cache_clear()
    yield
    reserved_module.reserved_segments.cache_clear()