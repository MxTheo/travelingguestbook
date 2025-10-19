import json
from django.urls import reverse
from faker import Faker
from conftest import street_activity
from travelingguestbook.factories import StreetActivityFactory, SWOTElementFactory

from streetactivity.models import SWOTElement
from streetactivity.views import handle_formulation_voting

fake = Faker()
Faker.seed(0)

class TestSWOTElementListView:
    """Test cases for SWOT element list view"""

    def test_list_view_returns_200(self, client):
        """Test that list view returns successful response"""
        activity = StreetActivityFactory()
        response = client.get(reverse('swotelement-list', kwargs={'pk': activity.pk}))
        
        assert response.status_code == 200
        assert 'elements' in response.context
    
    def test_list_view_with_activity_filter(self, client):
        """Test list view filtered by street activity"""
        activity = StreetActivityFactory()
        SWOTElementFactory.create_batch(3, street_activity=activity)

        response = client.get(reverse('swotelement-list', kwargs={'pk': activity.pk}))

        assert response.status_code == 200
        assert response.context['activity'] == activity
        assert len(response.context['elements']) == 3

    def test_list_view_sorting_options(self, client):
        """Test different sorting options"""
        # Create elements with different recognition counts
        activity = StreetActivityFactory()
        SWOTElementFactory(recognition_count=1, street_activity=activity)
        element_high = SWOTElementFactory(recognition_count=5, street_activity=activity)

        response = client.get(reverse('swotelement-list', kwargs={"pk":activity.pk}) + '?sort=popular')
        elements = response.context['elements']

        assert elements[0] == element_high  # Highest recognition first
    
    def test_list_view_type_filtering(self, client):
        """Test filtering by SWOT element type"""
        activity = StreetActivityFactory()
        SWOTElementFactory
        SWOTElementFactory(element_type='W', street_activity=activity)
        SWOTElementFactory(element_type='S', street_activity=activity)

        response = client.get(reverse('swotelement-list', kwargs={"pk":activity.pk}) + '?type=W')
        elements = response.context['elements']

        assert all(element.element_type == 'W' for element in elements)

    def test_empty_list_view(self, client):
        """Test list view with no elements"""
        activity = StreetActivityFactory()
        response = client.get(reverse('swotelement-list', kwargs={"pk":activity.pk}))

        assert response.status_code == 200
        assert len(response.context['elements']) == 0


class TestSWOTElementCreateView:
    """Test cases for SWOT element creation"""

    def test_create_view_returns_form(self, client):
        """Test that create view returns form on GET"""
        activity = StreetActivityFactory()

        response = client.get(reverse('create-swotelement', kwargs={'pk': activity.pk}))

        assert response.status_code == 200
        assert 'form' in response.context

    def test_create_view_creates_element(self, client):
        """Test that POST request creates new SWOT element"""
        activity = StreetActivityFactory()
        formulation_text = fake.text(max_nb_chars=200)

        response = client.post(
            reverse('create-swotelement', kwargs={'pk': activity.pk}),
            {
                'element_type': 'W',
                'formulation': formulation_text
            }
        )

        assert response.status_code == 302
        assert SWOTElement.objects.filter(
            street_activity=activity,
            formulation=formulation_text
        ).exists()
    
    def test_create_view_invalid_data(self, client):
        """Test create view with invalid form data"""
        activity = StreetActivityFactory()

        response = client.post(
            reverse('create-swotelement', kwargs={'pk': activity.pk}),
            {'element_type': 'X'}  # Invalid choice
        )

        assert response.status_code == 200  # Stays on form page
        assert 'form' in response.context
        assert response.context['form'].errors


class TestRecognitionFunctionality:
    """Test cases for recognition functionality"""

    def test_recognize_swotelement_success(self, client):
        """Test successful recognition of SWOT element"""
        element = SWOTElementFactory(recognition_count=0)

        response = client.post(
            reverse('recognize-swotelement', kwargs={'pk': element.pk}),
            content_type='application/json'
        )

        element.refresh_from_db()
        data = json.loads(response.content)

        assert response.status_code == 200
        assert data['success'] is True
        assert element.recognition_count == 1
        assert data['new_count'] == 1

    def test_recognize_swotelement_duplicate(self, client):
        """Test duplicate recognition prevention"""
        element = SWOTElementFactory(recognition_count=0)

        # First recognition
        client.post(reverse('recognize-swotelement', kwargs={'pk': element.pk}))

        # Second recognition (same session)
        response = client.post(
            reverse('recognize-swotelement', kwargs={'pk': element.pk}),
            content_type='application/json'
        )

        element.refresh_from_db()
        data = json.loads(response.content)

        assert response.status_code == 400
        assert 'error' in data
        assert element.recognition_count == 1

    def test_recognize_invalid_element(self, client):
        """Test recognition of non-existent element"""
        response = client.post(
            reverse('recognize-swotelement', kwargs={'pk': 99999}),
            content_type='application/json'
        )

        assert response.status_code == 404


class TestVotingFunctionality:
    """Test cases for formulation voting functionality"""

    def test_vote_formulation_success(self, client):
        """Test successful voting on formulation"""
        element = SWOTElementFactory(
            needs_voting=True,
            votes_current=0,
            votes_alternative=0
        )

        response = client.post(
            reverse('vote-formulation', kwargs={'pk': element.pk}),
            data=json.dumps({'vote_for_current': True}),
            content_type='application/json'
        )

        element.refresh_from_db()
        data = json.loads(response.content)

        assert response.status_code == 200
        assert data['success'] is True
        assert element.votes_current == 1
        assert element.votes_alternative == 0

    def test_vote_formulation_alternative(self, client):
        """Test voting for alternative formulation"""
        element = SWOTElementFactory(
            needs_voting=True,
            votes_current=0,
            votes_alternative=0
        )

        client.post(
            reverse('vote-formulation', kwargs={'pk': element.pk}),
            data=json.dumps({'vote_for_current': False}),
            content_type='application/json'
        )

        element.refresh_from_db()
        assert element.votes_current == 0
        assert element.votes_alternative == 1

    def test_vote_formulation_duplicate(self, client):
        """Test duplicate voting prevention"""
        element = SWOTElementFactory(needs_voting=True)

        # First vote
        client.post(
            reverse('vote-formulation', kwargs={'pk': element.pk}),
            data=json.dumps({'vote_for_current': True}),
            content_type='application/json'
        )

        # Second vote (same session)
        response = client.post(
            reverse('vote-formulation', kwargs={'pk': element.pk}),
            data=json.dumps({'vote_for_current': True}),
            content_type='application/json'
        )

        data = json.loads(response.content)
        assert response.status_code == 400
        assert 'error' in data

    def test_vote_formulation_no_voting_needed(self, client):
        """Test voting when no voting is needed"""
        element = SWOTElementFactory(needs_voting=False)

        response = client.post(
            reverse('vote-formulation', kwargs={'pk': element.pk}),
            data=json.dumps({'vote_for_current': True}),
            content_type='application/json'
        )

        data = json.loads(response.content)
        assert response.status_code == 400
        assert 'error' in data

    def test_vote_formulation_invalid_element(self, client):
        """Test voting on non-existent element"""
        response = client.post(
            reverse('vote-formulation', kwargs={'pk': 99999}),
            data=json.dumps({'vote_for_current': True}),
            content_type='application/json'
        )

        assert response.status_code == 404


class TestVotingCompletion:
    """Test cases for voting completion handling"""
    def test_handle_formulation_voting_alternative_wins(self):
        """Test voting completion when alternative wins"""
        element = SWOTElementFactory(
            formulation="Original",
            alternative_formulation="Better",
            votes_current=2,
            votes_alternative=3,
            needs_voting=True
        )

        handle_formulation_voting(element)
        element.refresh_from_db()

        assert element.formulation == "Better"
        assert element.alternative_formulation is None
        assert element.needs_voting is False
        assert element.votes_current == 0
        assert element.votes_alternative == 0
    
    def test_handle_formulation_voting_current_wins(self):
        """Test voting completion when current formulation wins"""
        element = SWOTElementFactory(
            formulation="Original",
            alternative_formulation="Worse",
            votes_current=4,
            votes_alternative=1,
            needs_voting=True
        )

        handle_formulation_voting(element)
        element.refresh_from_db()

        assert element.formulation == "Original"  # Unchanged
        assert element.alternative_formulation is None
        assert element.needs_voting is False

    def test_handle_formulation_voting_tie(self):
        """Test voting completion with tie votes"""

        element = SWOTElementFactory(
            formulation="Original",
            alternative_formulation="Alternative",
            votes_current=2,
            votes_alternative=2,
            needs_voting=True
        )

        handle_formulation_voting(element)
        element.refresh_from_db()

        assert element.formulation == "Original"
        assert element.needs_voting is False
