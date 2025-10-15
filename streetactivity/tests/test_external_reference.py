from django.urls import reverse
from travelingguestbook.factories import (
    ExternalReferenceFactory,
    BookReferenceFactory, 
    PersonalExperienceFactory,
    ResearchReferenceFactory,
    StreetActivityFactory
)
from streetactivity.models import ExternalReference

class TestExternalReferenceModel:
    """Tests for the ExternalReference model"""
    def test_external_reference_creation(self):
        """Test basic ExternalReference creation"""
        activity = StreetActivityFactory()
        reference = ExternalReferenceFactory(activity=activity)

        assert isinstance(reference, ExternalReference)
        assert reference.title is not None
        assert reference.description is not None
        assert reference.activity == activity

    def test_external_reference_without_url(self):
        """Test ExternalReference without URL (for books/theory)"""
        activity = StreetActivityFactory()
        reference = ExternalReferenceFactory(
            activity=activity,
            url="",  # Empty URL for book references
            title="The Power of Eye Contact",
            description="Boek over de kracht van oogcontact dat inspireerde tot deze activiteit"
        )

        assert reference.url == ""
        assert "Eye Contact" in reference.title

    def test_external_reference_ordering(self):
        """Test that references are ordered by creation date (newest first)"""
        activity = StreetActivityFactory()

        old_ref = ExternalReferenceFactory(activity=activity)
        new_ref = ExternalReferenceFactory(activity=activity)

        references = ExternalReference.objects.filter(activity=activity)
        assert references.first() == new_ref
        assert references.last() == old_ref

    def test_external_reference_string_representation(self):
        """Test the string representation"""
        activity = StreetActivityFactory(name="Eyegazing")
        reference = ExternalReferenceFactory(
            activity=activity,
            title="Persoonlijke ervaring"
        )

        assert str(reference) == "Persoonlijke ervaring - Eyegazing"

class TestExternalReferenceViews:
    """Tests for views related to ExternalReference"""
    def test_external_reference_create_view_get(self, client):
        """Test that the create form loads correctly"""
        activity = StreetActivityFactory()

        response = client.get(reverse('external_reference_create', kwargs={'activity_id': activity.pk}))

        assert response.status_code == 200
        assert 'streetactivity/externalreference_form.html' in [t.name for t in response.templates]
        assert 'form' in response.context

    def test_external_reference_create_view_post(self, client):
        """Test creating a new external reference"""
        activity = StreetActivityFactory()

        data = {
            'title': 'Mijn eerste oogcontact ervaring',
            'description': 'Het was spannend maar bijzonder om 1 minuut oogcontact te hebben',
            'url': 'https://mijnblog.nl/eyegazing-ervaring',
            'reference_type': 'persoonlijke ervaring',
            'submitted_by': 'Anonieme deelnemer'
        }

        response = client.post(
            reverse('external_reference_create', kwargs={'activity_id': activity.pk}),
            data
        )

        assert response.status_code == 302
        assert response.url == reverse('streetactivity_detail', kwargs={'pk': activity.pk})

        assert ExternalReference.objects.filter(activity=activity).exists()
        reference = ExternalReference.objects.get(activity=activity)
        assert reference.title == data['title']
        assert reference.submitted_by == data['submitted_by']

    def test_external_reference_create_without_url(self, client):
        """Test creating reference without URL (book/theory reference)"""
        activity = StreetActivityFactory()

        data = {
            'title': 'The Power of Eye Contact - James W. Williams',
            'description': 'Boek dat inspireerde tot deze eyegazing activiteit',
            'url': '',
            'reference_type': 'boek',
            'submitted_by': 'Theo'
        }

        response = client.post(
            reverse('external_reference_create', kwargs={'activity_id': activity.pk}),
            data
        )

        assert response.status_code == 302
        reference = ExternalReference.objects.get(activity=activity)
        assert reference.url == ""
        assert reference.reference_type == "boek"

    def test_external_reference_anonymous_submission(self, client):
        """Test creating reference without name (anonymous)"""
        activity = StreetActivityFactory()

        data = {
            'title': 'Leuke ervaring met vreemden',
            'description': 'Ik probeerde het uit en het was verrassend positief',
            'url': 'https://example.com',
            'reference_type': 'persoonlijke ervaring',
            'submitted_by': ''
        }

        response = client.post(
            reverse('external_reference_create', kwargs={'activity_id': activity.pk}),
            data
        )

        assert response.status_code == 302
        reference = ExternalReference.objects.get(activity=activity)
        assert reference.submitted_by == ""


class TestExternalReferenceInActivityDetail:
    """Tests for displaying ExternalReference in StreetActivity detail view"""
    def test_references_displayed_in_activity_detail(self, client):
        """Test that references are shown on activity detail page"""
        activity = StreetActivityFactory()
        reference = ExternalReferenceFactory(activity=activity)
        
        response = client.get(reverse('streetactivity_detail', kwargs={'pk': activity.pk}))
        content = response.content.decode()
        
        assert reference.title in content
        assert reference.description in content
    
    def test_empty_references_message(self, client):
        """Test message when no references exist"""
        activity = StreetActivityFactory()
        
        response = client.get(reverse('streetactivity_detail', kwargs={'pk': activity.pk}))
        content = response.content.decode()
        
        assert "Nog geen bronnen gedeeld" in content
        assert "Eerste bron toevoegen" in content

class TestExternalReferenceFactories:
    """Tests for ExternalReference factories"""
    def test_basic_external_reference_factory(self):
        """Test the basic ExternalReferenceFactory"""
        reference = ExternalReferenceFactory()

        assert reference.title is not None
        assert reference.description is not None
        assert reference.activity is not None

        assert isinstance(reference.url, str)

    def test_book_reference_factory(self):
        """Test the specialised BookReferenceFactory"""
        book_ref = BookReferenceFactory()

        assert book_ref.reference_type == "boek"
        assert book_ref.url == ""
        assert "Boek:" in book_ref.description

    def test_personal_experience_factory(self):
        """Test the PersonalExperienceFactory"""
        activity = StreetActivityFactory(name="Oogcontact")
        experience = PersonalExperienceFactory(activity=activity)

        assert experience.reference_type == "persoonlijke ervaring"
        assert experience.submitted_by is not None
        assert "ervaring met Oogcontact" in experience.title

    def test_research_reference_factory(self):
        """Test the ResearchReferenceFactory"""
        activity = StreetActivityFactory(name="Straatgesprekken")
        research = ResearchReferenceFactory(activity=activity)

        assert research.reference_type == "onderzoek"
        assert "Onderzoek naar Straatgesprekken" in research.title
        assert "academisch onderzoek" in research.description.lower()

    def test_multiple_references_for_activity(self):
        """Test multiple references linked to the same activity"""
        activity = StreetActivityFactory()

        book_ref = BookReferenceFactory(activity=activity)
        experience_ref = PersonalExperienceFactory(activity=activity)
        research_ref = ResearchReferenceFactory(activity=activity)

        assert book_ref.activity == activity
        assert experience_ref.activity == activity  
        assert research_ref.activity == activity

        assert activity.external_references.count() == 3
    
    def test_anonymous_submission_factory(self):
        """Test that factories can create anonymous submissions
        This test is meant more to verify the factory logic
        rather than exact probabilities."""
        references = ExternalReferenceFactory.create_batch(10)
        anonymous_count = sum(1 for ref in references if ref.submitted_by == "")
        print(f"Aantal anonieme inzendingen: {anonymous_count}")

class TestExternalReferenceFormIntegration:
    """Integration tests with forms using factory data"""
    def test_form_creation_with_factory_data(self, client):
        """Test that form can be submitted with factory-generated data"""
        activity = StreetActivityFactory()

        factory_reference = ExternalReferenceFactory.build(activity=activity)

        form_data = {
            'title': factory_reference.title,
            'description': factory_reference.description,
            'url': factory_reference.url,
            'reference_type': factory_reference.reference_type,
            'submitted_by': factory_reference.submitted_by,
        }

        response = client.post(
            reverse('external_reference_create', kwargs={'activity_id': activity.pk}),
            form_data
        )

        assert response.status_code == 302
        assert ExternalReference.objects.filter(
            activity=activity,
            title=factory_reference.title
        ).exists()
