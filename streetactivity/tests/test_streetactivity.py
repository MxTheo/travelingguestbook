from django.urls import reverse
from streetactivity.models import StreetActivity
from travelingguestbook.factories import StreetActivityFactory

class TestStreetActivityModel:
    '''Tests for the StreetActivity model.'''

    def test_streetactivity_detailview(self, client):
        '''Test the StreetActivity detail view to ensure it returns a 200 status code
        and contains the expected context.'''
        activity = StreetActivityFactory()
        response = client.get(f'/straatactiviteit/{activity.id}/')
        assert response.status_code == 200
        assert 'activity' in response.context

    def test_streetactivity_listview(self, client):
        '''Test the StreetActivity list view to ensure it returns a 200 status code
        and contains the expected context.'''
        # Maak eerst wat activiteiten aan
        StreetActivityFactory.create_batch(3)
        response = client.get('/straatactiviteiten')
        assert response.status_code == 200
        assert 'activities' in response.context
        assert len(response.context['activities']) == 3

    def test_streetactivity_createview(self, client):
        '''Test the StreetActivity create view to ensure it returns a 200 status code
        and contains the expected form in context.'''
        create_url = reverse("create-streetactivity")

        # Test POST request met valide data
        activity_data = StreetActivityFactory.build().__dict__
        for field in ['_state', 'id']:
            activity_data.pop(field, None)

        response = client.post(create_url, activity_data, follow=True)

        if hasattr(response, 'context') and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Form errors: {form.errors}")
            assert form.is_valid(), "Form is not valid"

        # Check of het redirect (meestal 302) en of object is aangemaakt
        assert response.status_code == 200
        assert StreetActivity.objects.count() == 1

    def test_streetactivity_updateview(self, client):
        '''Test the StreetActivity update view to ensure it returns a 200 status code
        and contains the expected form in context.'''
        activity = StreetActivityFactory()
        update_url = reverse("update-streetactivity", args=[activity.id])

        # Test POST request met updated data
        updated_data = {
            'name': 'Updated Activiteit',
            'description': activity.description,
            'method': activity.method,
            'question': activity.question,
            'supplies': activity.supplies,
            'difficulty': activity.difficulty,
            'chance': activity.chance,
            'needHelp': activity.needHelp
        }

        response = client.post(update_url, updated_data, follow=True)

        if hasattr(response, 'context') and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Form errors: {form.errors}")
            assert form.is_valid(), "Form is not valid"

        assert response.status_code == 200

        # Refresh from database en check of naam is geüpdatet
        activity.refresh_from_db()
        assert activity.name == 'Updated Activiteit'

    def test_streetactivity_deleteview(self, auto_login_user):
        '''Test the StreetActivity delete view to ensure it returns a 200 status code
        and contains the expected context.'''
        client, _ = auto_login_user()
        activity = StreetActivityFactory()

        # Controleer eerst dat het object bestaat
        assert StreetActivity.objects.filter(id=activity.id).exists()

        delete_streetactivity_url = reverse("delete-streetactivity", args=[activity.id])

        # Gebruik POST voor delete (Django gebruikt vaak POST voor delete bevestiging)
        response = client.post(delete_streetactivity_url)

        assert response.status_code == 302
        assert not StreetActivity.objects.filter(id=activity.id).exists()
        assert StreetActivity.objects.count() == 0
