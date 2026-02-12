import uuid
import pytest
from django.test import RequestFactory
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from streetactivity.views import AssignActivityToMomentView, SelectActivityForMomentView
from streetactivity.tests.test_moment_models import create_moment_data
from streetactivity.utils.session_helpers import clear_session_data
from streetactivity.models import Moment, Experience
from travelingguestbook.factories import ExperienceFactory, MomentFactory, StreetActivityFactory

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
        assert session['selected_activity_id'] == str(activity.id)

    def test_activity_from_selected_activity_id_is_retrieved_in_retrieve_activity(
            self,
            auto_login_user):
        """Given that the user has made a moment before and therefore the
        selected_activity_id is in session, test that retrieve_activity
        method fetches that activity of the moment before"""
        _, user = auto_login_user()
        StreetActivityFactory()
        StreetActivityFactory()
        activity = StreetActivityFactory(name="Selected Activity")
        request = RequestFactory().get('/')
        request.user = user
        request = add_middleware_to_request(request)

        request.session['selected_activity_id'] = str(activity.id)
        request.session.save()

        view = SelectActivityForMomentView()

        retrieved_activity = view.retrieve_activity(request)

        assert retrieved_activity.name == "Selected Activity"

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

        clear_session_data(request)

        assert 'moment_data' not in request.session
        assert 'selected_activity_id' not in request.session
        assert 'experience_id' not in request.session
        assert 'cancel_url' not in request.session

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

class TestShowActivityOnMomentForm:
    """Tests that the streetactivity is shown and selected on moment form when adding a moment to an experience"""
    def test_when_user_selected_activity_in_next_page(self, auto_login_user):
        """
        Given the user goes back from select activity in the moment form,
        by clicking the back button in browser
        test that the activity that is selected is shown on the moment form page
        """
        client, _ = auto_login_user()

        # Create experience and first moment with activity
        activity1 = StreetActivityFactory(name="Test1 Activity")

        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        session = client.session
        session['moment_data'] = moment_data
        session.save()

        url = reverse("add-first-moment-to-experience")
        client.get(url)

        url_select = reverse("select-activity-for-moment")
        client.get(url_select)
        # Select activity on the select page
        response = client.get(url_select, data={'activity_id': str(activity1.id)})


        assert response.status_code == 200
        # Go to previous page (browser back button)
        response = client.get(url)

        # Assert that the selected activity is shown on page
        assert response.status_code == 200
        content = response.content.decode()
        assert "Test1 Activity" in content

    def test_when_user_adds_second_moment(self, auto_login_user):
        """
        Given the user adds a second moment to experience,
        test that the streetactivity of the first moment is shown and selected in the moment form
        """
        client, user = auto_login_user()

        # Create experience and first moment with activity
        experience = ExperienceFactory(user=user)
        activity1 = StreetActivityFactory(name="Test1 Activity")
        MomentFactory(
            experience=experience,
            activity=activity1,
            report="First moment report",
            confidence_level=1,
            keywords="first,moment"
        )

        # Now add second moment
        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        session = client.session
        session['moment_data'] = moment_data
        session['experience_id'] = str(experience.id)
        session.save()

        url = reverse('add-moment-to-experience', kwargs={'experience_id': experience.id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()

        # Check that the activity of the first moment is shown and selected
        assert "Test1 Activity" in content

    def test_when_user_adds_third_moment(self, auto_login_user):
        """
        Given the user adds a third moment to experience,
        test that the streetactivity of the moment before (the second moment) is shown and selected in the moment form
        """
        client, user = auto_login_user()

        # Create experience and first two moments with activities
        experience = ExperienceFactory(user=user)
        activity1 = StreetActivityFactory(name="Activity 1")
        MomentFactory(
            experience=experience,
            activity=activity1,
            report="First moment report",
            confidence_level=1,
            keywords="first,moment"
        )
        activity2 = StreetActivityFactory(name="Activity 2")
        MomentFactory(
            experience=experience,
            activity=activity2,
            report="Second moment report",
            confidence_level=2,
            keywords="second,moment"
        )

        # Now add third moment
        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        session = client.session
        session['moment_data'] = moment_data
        session['experience_id'] = str(experience.id)
        session.save()

        url = reverse('add-moment-to-experience', kwargs={'experience_id': experience.id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()

        # Check that the activity of the second moment is shown and selected
        assert "Activity 2" in content

    def test_no_activity_selected_on_first_visit(self, auto_login_user):
        """
        Given the user adds a moment to an experience with no previous moments,
        test that no streetactivity is pre-selected in the moment form
        """
        client, _ = auto_login_user()
        moment_data = create_moment_data()
        moment_data.pop('activity', None)

        session = client.session
        session['moment_data'] = moment_data
        session.save()

        url = reverse("add-first-moment-to-experience")
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        # Er zou geen activiteit geselecteerd moeten zijn
        assert 'selected="selected"' not in content

    def test_initial_activity_selected_from_session(self, auto_login_user):
        """Given the user has selected an activity in the select activity page,
test that this activity is pre-selected in the moment form page when going back"""
        client, _ = auto_login_user()
        # Setup user en login
        client, _ = auto_login_user()

        # Maak een activiteit aan
        activity = StreetActivityFactory(name="Test Activity")
        experience = ExperienceFactory()

        # Zet de activiteit in de sessie als geselecteerd
        session = client.session
        session['selected_activity_id'] = activity.id
        session.save()

        # Ga naar de add moment pagina
        url = reverse("add-moment-to-experience", kwargs={"experience_id": experience.id})  # pas aan indien nodig
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()

        # Controleer of de activiteit naam in de pagina staat (voorselectie zichtbaar)
        assert "Test Activity" in content

    def test_back_url_with_no_experience_id(self):
        """Given no experience id is in session,
        test that the created back_url goes to add-first-moment-to-experience"""
        view = SelectActivityForMomentView()
        request = RequestFactory().get('/')
        request.session = {}
        view.request = request
        back_url = view.create_back_url()
        assert back_url == reverse('add-first-moment-to-experience')


    def test_back_url_with_experience_id(self):
        """Given experience id is in session,
        test that the created back_url goes to add-moment-to-experience"""
        experience = ExperienceFactory()
        view = SelectActivityForMomentView()
        request = RequestFactory().get('/')
        request.session = {'experience_id': experience.id}
        view.request = request

        back_url = view.create_back_url()
        assert back_url == reverse('add-moment-to-experience', kwargs={'experience_id': experience.id})

class TestAssignActivityToMomentViewValidation:
    """Tests for the validation logic in AssignActivityToMomentView,
    specifically the redirect_to_moment_form_if_missing_data method.
    This method checks if the necessary data is present before creating a moment,
    and redirects to the moment form with appropriate messages if data is missing."""
    @pytest.fixture
    def view(self):
        """Create an instance of AssignActivityToMomentView with a request
        that has session and messages middleware."""
        rf = RequestFactory()
        request = rf.get("/")
        request = add_middleware_to_request(request)

        view = AssignActivityToMomentView()
        view.request = request
        return view

    def test_redirect_when_missing_moment_data(self, view):
        """Test that if moment_data is None, the user is redirected to the moment form with a message."""
        redirect_response = view.redirect_to_moment_form_if_missing_data(
            moment_data=None,
            selected_activity_id=1,
            experience_id=None,
        )
        assert redirect_response.status_code == 302
        assert reverse("add-first-moment-to-experience") in redirect_response.url

        message_list = list(messages.get_messages(view.request))
        assert any("Niet alles ingevuld" in m.message for m in message_list)

    def test_redirect_when_missing_required_fields(self, view):
        """Test that if there is no report and keywords,
        the user is redirected to the moment form with a message"""
        moment_data = {"report": "", "keywords": ""}
        redirect_response = view.redirect_to_moment_form_if_missing_data(
            moment_data=moment_data,
            selected_activity_id=1,
            experience_id=None,
        )
        assert redirect_response.status_code == 302
        assert reverse("add-first-moment-to-experience") in redirect_response.url

        message_list = list(messages.get_messages(view.request))
        assert any("Niet alles ingevuld" in m.message for m in message_list)
        assert "report" in message_list[1].message

    def test_redirect_when_missing_selected_activity(self, view):
        """Test when the user has not selected an activity,
        the user is redirected to the moment form with a message"""
        moment_data = {"report": "some report", "keywords": "some keywords"}
        redirect_response = view.redirect_to_moment_form_if_missing_data(
            moment_data=moment_data,
            selected_activity_id=None,
            experience_id=None,
        )
        assert redirect_response.status_code == 302
        assert reverse("add-first-moment-to-experience") in redirect_response.url

        message_list = list(messages.get_messages(view.request))
        assert any("Selecteer een activiteit" in m.message for m in message_list)

    def test_no_redirect_when_all_data_present(self, view):
        """Test when all data is present,
        the user is not redirected to the moment form with a message"""
        moment_data = {"report": "some report", "keywords": "some keywords"}
        redirect_response = view.redirect_to_moment_form_if_missing_data(
            moment_data=moment_data,
            selected_activity_id=1,
            experience_id=None,
        )
        assert redirect_response is None

