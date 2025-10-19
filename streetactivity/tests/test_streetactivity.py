import pytest
from django.urls import reverse
from streetactivity.models import StreetActivity, SWOTElement
from travelingguestbook.factories import StreetActivityFactory, SWOTElementFactory

class TestStreetActivityModel:
    """Tests for the StreetActivity model."""
    def test_streetactivity_listview(self, client):
        """Test the StreetActivity list view to ensure it returns a 200 status code
        and contains the expected context."""
        # Maak eerst wat activiteiten aan
        StreetActivityFactory.create_batch(3)
        response = client.get(reverse("streetactivity_list"))
        assert response.status_code == 200
        assert "activities" in response.context
        assert len(response.context["activities"]) == 3

    def test_streetactivity_createview(self, client):
        """Test the StreetActivity create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        create_url = reverse("create-streetactivity")

        activity_data = StreetActivityFactory.build().__dict__
        for field in ["_state", "id"]:
            activity_data.pop(field, None)

        response = client.post(create_url, activity_data, follow=True)

        assert response.status_code == 200
        assert StreetActivity.objects.count() == 1

    def test_streetactivity_updateview(self, client):
        """Test the StreetActivity update view to ensure it returns a 200 status code
        and contains the expected form in context."""
        activity = StreetActivityFactory()
        update_url = reverse("update-streetactivity", args=[activity.id])

        updated_data = {
            "name": "Updated Activiteit",
            "description": activity.description,
            "method": activity.method,
            "question": activity.question,
            "supplies": activity.supplies,
            "difficulty": activity.difficulty,
            "chance": activity.chance,
            "needHelp": activity.needHelp,
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        activity.refresh_from_db()
        assert activity.name == "Updated Activiteit"

    def test_streetactivity_deleteview(self, client):
        """Test the StreetActivity delete view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()

        assert StreetActivity.objects.filter(id=activity.id).exists()

        delete_streetactivity_url = reverse("delete-streetactivity", args=[activity.id])

        response = client.post(delete_streetactivity_url)

        assert response.status_code == 302
        assert not StreetActivity.objects.filter(id=activity.id).exists()
        assert StreetActivity.objects.count() == 0

    def test_streetactivity_string(self):
        """Test string reprensentation of streetactivity"""
        activity = StreetActivityFactory(name="test")
        assert str(activity) == "test"

class TestStreetActivityListView:
    """Tests for the StreetActivity list view."""

    def test_list_view_returns_200(self, client):
        """Test that the list view returns a 200 status code"""
        response = client.get(reverse("streetactivity_list"))
        assert response.status_code == 200

    def test_list_view_uses_correct_template(self, client):
        """Test that the list view uses the correct template"""
        response = client.get(reverse("streetactivity_list"))
        assert "streetactivity/streetactivity_list.html" in [
            t.name for t in response.templates
        ]

    def test_list_view_shows_activities(self, client):
        """Test that activities are displayed in the list view"""
        # Maak test activiteiten aan met factory
        StreetActivityFactory(name="Test Activiteit 1", needHelp=False)
        StreetActivityFactory(name="Test Activiteit 2", needHelp=True)

        response = client.get(reverse("streetactivity_list"))
        content = response.content.decode()

        assert "Test Activiteit 1" in content
        assert "Test Activiteit 2" not in content

    def test_list_view_pagination(self, client):
        """Test that pagination works correctly"""
        # Maak meer activiteiten aan voor paginatie test
        for i in range(15):
            StreetActivityFactory(name=f"Pagination Test {i}", needHelp=False)

        response = client.get(reverse("streetactivity_list"))

        assert response.context["is_paginated"]
        assert len(response.context["activities"]) == 10

    def test_list_view_ordering(self, client):
        """Test that activities are ordered by name"""
        StreetActivityFactory(name="Zebra Activiteit", needHelp=False)
        StreetActivityFactory(name="Alpha Activiteit", needHelp=False)
        StreetActivityFactory(name="Beta Activiteit", needHelp=False)

        response = client.get(reverse('streetactivity_list'))
        activities = list(response.context['activities'])

        names = [activity.name for activity in activities]
        assert names == sorted(names)

    def test_list_view_context_data(self, client):
        """Test that the correct context data is provided"""
        StreetActivityFactory(needHelp=False)

        response = client.get(reverse("streetactivity_list"))
        context = response.context

        assert "activities" in context
        assert "help_needed_count" in context
        assert "has_help_needed" in context

    def test_help_needed_count_in_context(self, client):
        """Test that help_needed_count is calculated correctly"""
        # Maak 2 activiteiten zonder hulp nodig, 3 met hulp nodig
        StreetActivityFactory.create_batch(2, needHelp=False)
        StreetActivityFactory.create_batch(3, needHelp=True)

        response = client.get(reverse("streetactivity_list"))
        assert response.context["help_needed_count"] == 3

    def test_has_help_needed_in_context_when_help_needed_exists(self, client):
        """Test that has_help_needed is True when there are activities needing help"""
        StreetActivityFactory(needHelp=True)
        StreetActivityFactory(needHelp=False)
        
        response = client.get(reverse('streetactivity_list'))

        assert response.context['has_help_needed']
        assert len(response.context['activities']) == 1

    def test_has_help_needed_false_when_no_help_needed(self, client):
        """Test that has_help_needed is False when there are no activities needing help"""
        StreetActivityFactory.create_batch(3, needHelp=False)

        response = client.get(reverse("streetactivity_list"))
        assert not response.context["has_help_needed"]

class TestStreetActivityListViewFilter:
    """Tests for filtering activities in the StreetActivity list view."""

    def test_filter_help_needed(self, client):
        """Test filter activities needing help"""
        StreetActivityFactory(name="Hulp Nodig", needHelp=True)
        StreetActivityFactory(name="Werkende Activiteit", needHelp=False)

        response = client.get(reverse('streetactivity_list') + '?filter=help_needed')

        activities = list(response.context['activities'])  # Convert to list to avoid queryset issues
        assert len(activities) == 1
        assert activities[0].name == "Hulp Nodig"
        assert activities[0].needHelp

    def test_default_filter_shows_no_help_needed(self, client):
        """Test that by default only activities without help needed are shown"""
        StreetActivityFactory(name="Hulp Nodig", needHelp=True)
        StreetActivityFactory(name="Werkende Activiteit", needHelp=False)

        response = client.get(reverse('streetactivity_list'))

        activities = list(response.context['activities'])  # Convert to list
        assert len(activities) == 1
        assert activities[0].name == "Werkende Activiteit"
        assert not activities[0].needHelp

    def test_empty_results_when_no_activities_match_filter(self, client):
        """Test that no activities are shown when none match the filter"""
        # Alleen activiteiten met hulp nodig
        StreetActivityFactory.create_batch(2, needHelp=True)

        # Standaard filter zou geen resultaten moeten tonen
        response = client.get(reverse("streetactivity_list"))

        activities = response.context["activities"]
        assert activities.count() == 0

    def test_help_needed_filter_shows_all_help_needed(self, client):
        """Test that help_needed filter shows all activities needing help"""
        # Maak mix van activiteiten
        StreetActivityFactory.create_batch(3, needHelp=True)
        StreetActivityFactory.create_batch(2, needHelp=False)

        response = client.get(reverse("streetactivity_list") + "?filter=help_needed")

        activities = response.context["activities"]
        assert activities.count() == 3
        assert all(activity.needHelp for activity in activities)

@pytest.fixture
def help_needed_activities():
    """Fixture voor activiteiten die hulp nodig hebben"""
    return StreetActivityFactory.create_batch(3, needHelp=True)

@pytest.fixture
def working_activities():
    """Fixture voor werkende activiteiten"""
    return StreetActivityFactory.create_batch(2, needHelp=False)

class TestWithFixtures:
    """Tests met gebruik van fixtures voor activiteiten"""

    def test_context_with_fixtures(
        self, client, help_needed_activities, working_activities
    ):
        """Test context data met fixtures"""
        response = client.get(reverse("streetactivity_list"))

        assert response.context["help_needed_count"] == 3
        assert response.context["has_help_needed"]
        assert len(response.context["activities"]) == 2  # Alleen werkende activiteiten

    def test_filter_with_fixtures(
        self, client, help_needed_activities, working_activities
    ):
        """Test filter functionaliteit met fixtures"""
        response = client.get(reverse("streetactivity_list") + "?filter=help_needed")

        activities = response.context["activities"]
        assert activities.count() == 3
        assert all(activity.needHelp for activity in activities)

    def test_context_help_needed_count_with_fixtures(
        self, client, help_needed_activities, working_activities
    ):
        """Test that help_needed_count is calculated correctly with fixtures"""
        """Test dat help_needed_count correct wordt berekend met fixtures"""
        response = client.get(reverse("streetactivity_list"))

        # help_needed_count moet het totaal zijn van alle activiteiten met needHelp=True
        assert response.context["help_needed_count"] == 3
        # has_help_needed moet True zijn omdat er activiteiten met needHelp bestaan
        assert response.context["has_help_needed"]
        # Alleen werkende activiteiten worden getoond in de standaard view
        assert len(response.context["activities"]) == 2

    def test_filter_functionality_with_fixtures(
        self, client, help_needed_activities, working_activities
    ):
        """Test filter functionality with fixtures"""
        # Test standaard filter (zonder needHelp)
        response_default = client.get(reverse("streetactivity_list"))
        activities_default = list(response_default.context["activities"])
        assert len(activities_default) == 2
        assert all(not activity.needHelp for activity in activities_default)

        # Test help_needed filter
        response_help = client.get(
            reverse("streetactivity_list") + "?filter=help_needed"
        )
        activities_help = list(response_help.context["activities"])
        assert len(activities_help) == 3
        assert all(activity.needHelp for activity in activities_help)

class TestSWOTModels:
    def test_swot_element_creation(self):
        activity = StreetActivityFactory()
        element = SWOTElementFactory(
            street_activity=activity,
            element_type='S',
            formulation="Test strength"
        )
        
        assert element.street_activity == activity
        assert element.element_type == 'S'
        assert element.formulation == "Test strength"

    def test_swot_element_str(self):
        """Test the string representation of SWOT element"""
        element = SWOTElementFactory(formulation="Community engagement")
        assert "Community engagement" in str(element)


class TestSWOTViews:
    def test_swotelement_create_view(self, client):
        activity = StreetActivityFactory()

        response = client.get(reverse('create-swotelement', kwargs={'pk': activity.pk}))
        assert response.status_code == 200

        data = {
            'element_type': 'S',
            'formulation': 'New strength'
        }
        response = client.post(reverse('create-swotelement', kwargs={'pk': activity.pk}), data)
        assert response.status_code == 302
        assert SWOTElement.objects.filter(street_activity=activity).exists()
