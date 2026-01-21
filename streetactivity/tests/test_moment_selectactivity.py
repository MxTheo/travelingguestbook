import uuid
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from streetactivity.views import AssignActivityToMomentView
from streetactivity.tests.test_moment_models import create_moment_data
from streetactivity.models import Moment, Experience
from travelingguestbook.factories import ExperienceFactory, StreetActivityFactory

class TestSelectActivityForMoment:
    """Test the session driven flow to select streetactivity for moments"""
    def test_submit_moment_without_activity(self, auto_login_user):
        """
        Given a moment without activity selected,
        when the user posts the form,
        then the response redirects to the activity select page,
        and the moment data is saved in the session.
        """
        client, _ = auto_login_user()
        url_add_moment = reverse("add-first-moment-to-experience")
        moment_data = create_moment_data()
        # Remove activity to simulate no activity selected yet
        moment_data.pop('activity', None)

        response = client.post(url_add_moment, data=moment_data)

        assert response.status_code == 302
        assert response.url == reverse('select-activity-for-moment')

        # Check that moment_data is saved in session
        session_moment_data = client.session.get('moment_data')
        assert session_moment_data is not None
        for key in moment_data:
            assert session_moment_data[key] == moment_data[key]

    def test_get_select_activity_page(self, auto_login_user):
        """
        Given a session with moment_data and experience_id,
        when the user requests the activity select page,
        then the page loads and contains the list of activities.
        """
        client, _ = auto_login_user()

        # Create some activities
        activities = StreetActivityFactory.create_batch(3)

        # Setup session data
        moment_data = create_moment_data()
        moment_data.pop('activity', None)
        client.session['moment_data'] = moment_data
        client.session['experience_id'] = 'some-uuid-string'

        url = reverse('select-activity-for-moment')
        response = client.get(url)

        assert response.status_code == 200
        # Check that all activities are in the response context
        for activity in activities:
            assert activity.name in response.content.decode()

    def test_post_without_activity_id(self, auto_login_user):
        """
        When no activity_id is posted,
        the user is redirected back with an error message.
        """
        client, _ = auto_login_user()
        url = reverse('select-activity-for-moment')

        response = client.post(url, data={})

        assert response.status_code == 302
        assert response.url == url  # redirect back to same page

        messages = list(get_messages(response.wsgi_request))
        assert any("Geen activiteit geselecteerd" in str(m) for m in messages)

    def test_post_with_valid_activity_id(self, auto_login_user):
        """
        When a valid activity_id is posted,
        it is saved in the session and redirects to assign activity view.
        """
        client, _ = auto_login_user()
        activity = StreetActivityFactory()
        url = reverse('select-activity-for-moment')

        # Prepare session data (moment_data and experience_id) to simulate flow
        moment_data = create_moment_data()
        moment_data.pop('activity', None)
        client.session['moment_data'] = moment_data
        client.session['experience_id'] = 'some-uuid-string'

        response = client.post(url, data={'activity_id': str(activity.id)})

        assert response.status_code == 302
        assert response.url == reverse('assign-activity-to-moment')

        # Check session has selected_activity_id saved as int
        session = client.session
        assert session['selected_activity_id'] == activity.id

class TestAssignActivityToMomentView:
    """Tests for AssignActivityToMomentView to ensure it uses session data correctly"""
    def test_redirect_if_session_data_missing(self, auto_login_user):
        """Given that session data is missing,
        test that user is redirected towards adding a first moment"""
        client, _ = auto_login_user()

        # No moment_data and selected_activity_id in session
        url = reverse('assign-activity-to-moment')
        response = client.get(url)

        assert response.status_code == 302
        # Redirect to add-first-moment-to-experience (experience_id not in session)
        assert response.url == reverse('add-first-moment-to-experience')

    def test_create_experience_and_moment(self, auto_login_user):
        """Given that no experience and moment exists, 
        test that moment and experience only created"""
        client, _ = auto_login_user()
        activity = StreetActivityFactory()

        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        session = client.session
        session['moment_data'] = moment_data
        session['experience_id'] = None
        session['selected_activity_id'] = activity.id
        session.save()

        url = reverse('assign-activity-to-moment')
        response = client.get(url)

        assert response.status_code == 302
        experience = Experience.objects.first()
        moment = Moment.objects.first()
        assert experience is not None
        assert moment is not None
        assert moment.experience == experience
        assert moment.activity == activity
        assert moment.report == moment_data['report']
        assert response.url == reverse('experience-detail', kwargs={'pk': experience.id})

    def test_redirect_to_moment_form_if_moment_data_is_missing(self, rf, auto_login_user):
        """Test redirect_to_moment_form_if_missing_data method behavior with missing data"""
        _, user = auto_login_user()
        view = AssignActivityToMomentView()
        view.request = rf.get('/')
        view.request.user = user
        view.request = add_middleware_to_request(view.request)

        response = view.redirect_to_moment_form_if_missing_data(None, '1', None)

        assert response.status_code == 302
        assert reverse('add-first-moment-to-experience') in response.url

    def test_redirect_to_moment_form_if_report_is_missing(self, rf, auto_login_user):
        """
        Test that redirect_to_moment_form_if_missing_data redirects to moment form
        if 'report' is missing or empty in moment_data.
        """
        _, user = auto_login_user()
        request = rf.get('/')
        request.user = user
        request = add_middleware_to_request(request)

        view = AssignActivityToMomentView()
        view.request = request

        moment_data = {
            'keywords': 'some,keywords',
            'confidence_level': 3,
            'from_practitioner': True,
        }
        selected_activity_id = 1
        experience_id = None

        response = view.redirect_to_moment_form_if_missing_data(
            moment_data,
            selected_activity_id,
            experience_id)
        assert response is not None
        assert response.status_code == 302
        assert reverse('add-first-moment-to-experience') in response.url


    def test_redirect_to_moment_form_if_keywords_are_missing(self, rf, auto_login_user):
        """
        Test that redirect_to_moment_form_if_missing_data redirects to moment form
        if 'keywords' is missing or empty in moment_data.
        """
        _, user = auto_login_user()
        request = rf.get('/')
        request.user = user
        request = add_middleware_to_request(request)

        view = AssignActivityToMomentView()
        view.request = request

        moment_data = {
            'report': 'Some report',
            'confidence_level': 3,
            'from_practitioner': True,
        }
        selected_activity_id = 1
        experience_id = None

        response = view.redirect_to_moment_form_if_missing_data(
            moment_data, selected_activity_id,
            experience_id)
        assert response is not None
        assert response.status_code == 302
        assert reverse('add-first-moment-to-experience') in response.url

    def test_redirect_to_moment_form_if_selected_activity_id_is_missing_but_experience_id_present(
            self,
            rf,
            auto_login_user):
        """Given no activity_id but only experience_id,
        test redirect to moment form"""
        _, user = auto_login_user()
        view = AssignActivityToMomentView()
        view.request = rf.get('/')
        view.request.user = user
        view.request = add_middleware_to_request(view.request)

        fake_uuid = str(uuid.uuid4())
        response = view.redirect_to_moment_form_if_missing_data(
            {'report': 'x', 'keywords':'x'},
            None,
            fake_uuid)
        assert response.status_code == 302
        assert reverse('add-moment-to-experience',
                       kwargs={'experience_id': fake_uuid}) in response.url

    def test_no_redirect_to_moment_form_if_all_data_present(self, rf, auto_login_user):
        """Given all the data,
        test that no response is given"""
        user = auto_login_user()[1]
        view = AssignActivityToMomentView()
        view.request = rf.get('/')
        view.request.user = user
        view.request = add_middleware_to_request(view.request)

        fake_uuid = str(uuid.uuid4())
        response = view.redirect_to_moment_form_if_missing_data(
            {'report': 'x', 'keywords':'x'},
            '123',
            fake_uuid)
        assert response is None

    def test_get_existing_experience(self, auto_login_user):
        """Given an existing experience_id,
        test if that experience is fetched"""
        user = auto_login_user()[1]
        view = AssignActivityToMomentView()

        experience = Experience.objects.create(user=user)

        exp, exp_id = view.get_or_create_experience(experience.id, user)
        assert exp == experience
        assert exp_id == str(experience.id)

    def test_create_experience_with_no_id(self, auto_login_user):
        """Given no experience_id,
        test if it creates an experience"""
        user = auto_login_user()[1]
        view = AssignActivityToMomentView()

        exp, exp_id = view.get_or_create_experience(None, user)
        assert exp.user == user
        assert isinstance(exp_id, str)

    def test_create_experience_with_false_id(self, auto_login_user):
        """Given a non-existing experience_id,
        test if it creates an experience"""
        user = auto_login_user()[1]
        view = AssignActivityToMomentView()
        false_uuid = str(uuid.uuid4())

        exp, exp_id = view.get_or_create_experience(false_uuid, user)
        assert exp.user == user
        assert isinstance(exp_id, str)

    def test_create_moment_creates_instance(self, auto_login_user):
        """Given correct moment data,
        test if a moment instance is created"""
        user = auto_login_user()[1]
        view = AssignActivityToMomentView()
        view.request = RequestFactory().get('/')
        view.request.user = user

        experience = ExperienceFactory(user=user)
        activity = StreetActivityFactory(
            name="Test",
            description="Desc",
            method="invite",
            question="Q?",
            supplies="None"
        )
        moment_data = {
            'report': 'Report text',
            'confidence_level': 2,
            'from_practitioner': True,
            'keywords': 'key1,key2',
        }

        moment = view.create_moment(moment_data, experience, activity)
        assert moment.pk is not None
        assert moment.experience == experience
        assert moment.activity == activity
        assert moment.report == 'Report text'

    def test_clear_session_data(self, rf):
        """Given data stored in session,
        test if the session is cleared"""
        request = rf.get('/')
        request.session = {}
        request.session['moment_data'] = 'data'
        request.session['selected_activity_id'] = 1
        request.session['experience_id'] = 'uuid'
        request.session['cancel_url'] = '/some-url/'

        view = AssignActivityToMomentView()
        view.clear_session_data(request)

        assert 'moment_data' not in request.session
        assert 'selected_activity_id' not in request.session
        assert 'experience_id' not in request.session
        assert 'cancel_url' not in request.session

    def test_assign_activity_to_moment_post_creates_moment(self, auto_login_user):
        """Given session data with moment_data and no experience,
        when posting with a selected activity,
        test that a new experience and moment are created,
        and the user is redirected to the experience detail page."""
        client = auto_login_user()[0]

        activity = StreetActivityFactory()

        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        session = client.session
        session['moment_data'] = moment_data
        session['experience_id'] = None  # Nieuwe experience verwacht
        session.save()

        url = reverse('assign-activity-to-moment')

        # POST met geselecteerde activiteit
        response = client.post(url, data={'activity_id': str(activity.id)})

        # Check redirect naar experience detail
        assert response.status_code == 302
        experience = Experience.objects.first()
        moment = Moment.objects.first()

        assert experience is not None
        assert moment is not None
        assert moment.experience == experience
        assert moment.activity == activity
        assert moment.report == moment_data['report']
        assert response.url == reverse('experience-detail', kwargs={'pk': experience.id})

    def test_lvl_up_on_moment_creation(self, auto_login_user):
        """Given a user creating a moment with confidence level,
        test that XP and level are processed correctly."""
        client, user = auto_login_user()

        activity = StreetActivityFactory()

        moment_data = create_moment_data()
        moment_data.pop('activity', None)
        confidence_level = 0
        moment_data['confidence_level'] = confidence_level

        session = client.session
        session['moment_data'] = moment_data
        session['experience_id'] = None
        session.save()

        url = reverse('assign-activity-to-moment')

        # Capture initial XP and level
        initial_xp = user.profile.xp
        initial_level = user.profile.lvl

        # POST met geselecteerde activiteit
        client.post(url, data={'activity_id': str(activity.id)})

        # Refresh user profile
        user.profile.refresh_from_db()

        # Check that XP and level have been updated
        assert user.profile.xp > initial_xp
        assert user.profile.lvl >= initial_level

def add_middleware_to_request(request):
    """Add session and message middleware to the request for testing purposes."""
    def get_response(req):
        return None
    session_middleware = SessionMiddleware(get_response)
    session_middleware.process_request(request)
    request.session.save()

    message_middleware = MessageMiddleware(get_response)
    message_middleware.process_request(request)
    request._messages = messages.storage.default_storage(request)

    return request
