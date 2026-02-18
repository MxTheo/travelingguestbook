import uuid
from django.urls import reverse
from streetactivity.utils.session_helpers import (
    determine_cancel_url, setup_session_for_cancel, cancel_moment_creation
)
from travelingguestbook.factories import ExperienceFactory

class TestDetermineCancelUrl:
    """Test suite for determine_cancel_url function."""
    def test_with_experience_id_in_kwargs(self, rf):
        """Test when experience_id is in view kwargs."""
        request = rf.get('/')
        request.session = {}

        fake_uuid = uuid.uuid4()
        kwargs = {'experience_id': fake_uuid}
        result = determine_cancel_url(kwargs)

        assert 'straatactiviteiten/ervaring' in result
        assert str(fake_uuid) in result

    def test_fallback_to_home(self, rf):
        """Test fallback to home when no other conditions match."""
        request = rf.get('/')
        request.session = {}

        result = determine_cancel_url({})

        assert result == reverse('home')

class TestSetupSessionForCancel:
    """Test suite for setup_session_for_cancel function."""

    def test_setup_for_experience_flow(self, rf):
        """Test session setup for experience multi-step flow."""
        request = rf.get('/')
        request.session = {}

        fake_uuid = uuid.uuid4()
        setup_session_for_cancel(request, {'experience_id': fake_uuid})

        assert 'cancel_url' in request.session

    def test_setup_for_first_moment_experience(self, rf):
        """Test session setup for adding first moment to experience."""
        request = rf.get(reverse('add-first-moment-to-experience'))
        request.session = {}

        setup_session_for_cancel(request, {})

        assert 'cancel_url' in request.session

    def test_no_setup_for_regular_moment(self, rf):
        """Test no session setup for regular moment creation."""
        request = rf.get('/moment/nieuw/')
        request.session = {}

        setup_session_for_cancel(request, {})

        assert 'cancel_url' not in request.session

class TestCancelMomentCreation:
    """Test suite for cancel_moment_creation view."""
    def test_cancel_moment_creation_clears_session_and_redirects(self, rf):
        """Test that cancel_moment_creation clears session data and redirects."""
        request = rf.get('/moment/annuleer')
        request.session = {
            'cancel_url': '/some-url/',
            'moment_data': {'report': 'test'},
            'selected_activity_id': 1,
            'experience_id': 'uuid',
            'from_experience': True,
        }

        response = cancel_moment_creation(request)

        # Check that session data is cleared
        assert 'cancel_url' not in request.session
        assert 'moment_data' not in request.session
        assert 'selected_activity_id' not in request.session
        assert 'experience_id' not in request.session
        assert 'from_experience' not in request.session

        # Check that it redirects to the cancel_url
        assert response.status_code == 302
        assert response.url == '/some-url/'

class TestIntegrationCancelMoment:
    """Integration tests for cancel moment functionality in views."""

    def test_cancel_url_present_from_experience_moment_creation(self, auto_login_user):
        """Given a user adding a moment to an experience,
        test if a cancel url is present"""
        client, _ = auto_login_user()

        url_add_moment = reverse('add-first-moment-to-experience')

        # Start experience moment creation
        response = client.get(url_add_moment)
        assert response.status_code == 200

        # Check session for cancel_url
        session = client.session
        assert 'cancel_url' in session

    def test_cancel_from_adding_first_moment_to_experience(self, auto_login_user):
        """Given the user cancels the first moment creation,
        test if cancelling redirects to the home page
        """
        client, _ = auto_login_user()

        url_add_moment = reverse('add-first-moment-to-experience')

        # Start experience moment creation
        response = client.get(url_add_moment)
        assert response.status_code == 200

        # Perform cancel action
        cancel_url = client.session['cancel_url']
        response = client.get(cancel_url)
        assert response.status_code == 200
        assert response.request['PATH_INFO'] == reverse('home')


    def test_cancel_from_adding_second_moment_to_experience(self, auto_login_user):
        """
        Given the user cancels the second moment creation,
        test if cancelling redirects to the experience detail page
        """
        client, user = auto_login_user()

        experience = ExperienceFactory(user=user)

        url_add_moment = reverse('add-moment-to-experience',
                                 kwargs={'experience_id': experience.id})

        # Start experience moment creation
        response = client.get(url_add_moment)
        assert response.status_code == 200

        # Perform cancel action
        cancel_url = client.session['cancel_url']
        response = client.get(cancel_url)
        assert response.status_code == 200
        assert f'/ervaring/{experience.id}/' in response.request['PATH_INFO']

    def test_cancel_from_adding_second_moment_with_activity_selected(self, auto_login_user):
        """
        Given the user cancels the second moment creation with an activity selected,
        tests if cancelling redirects to the experience detail page
        """
        client, user = auto_login_user()

        experience = ExperienceFactory(user=user)

        url_add_moment = reverse('add-moment-to-experience',
                                 kwargs={'experience_id': experience.id})

        # Start experience moment creation
        response = client.get(url_add_moment)
        assert response.status_code == 200

        # Simulate activity selection in session
        session = client.session
        session['selected_activity_id'] = 1
        session.save()

        # Perform cancel action
        cancel_url = client.session['cancel_url']
        response = client.get(cancel_url)
        assert response.status_code == 200
        assert f'/ervaring/{experience.id}/' in response.request['PATH_INFO']

    def test_two_cancellations_from_different_entry_points(self, auto_login_user):
        """
        Given a user cancels the first moment creation
        and then the user starts an experience and cancels the second moment creation,
        tests if cancelling redirects to the experience detail page
        """
        client, user = auto_login_user()

        # First cancellation from adding first moment
        url_add_first_moment = reverse('add-first-moment-to-experience')

        response = client.get(url_add_first_moment)
        assert response.status_code == 200

        cancel_url_first = client.session['cancel_url']
        response = client.get(cancel_url_first)
        assert response.status_code == 200
        assert response.request['PATH_INFO'] == reverse('home')

        # Now start an experience and add second moment
        experience = ExperienceFactory(user=user)
        url_add_second_moment = reverse('add-moment-to-experience',
                                        kwargs={'experience_id': experience.id})

        response = client.get(url_add_second_moment)
        assert response.status_code == 200

        cancel_url_second = client.session['cancel_url']
        response = client.get(cancel_url_second)
        assert response.status_code == 200
        assert f'/ervaring/{experience.id}/' in response.request['PATH_INFO']
