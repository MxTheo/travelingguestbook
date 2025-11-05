from travelingguestbook.factories import ExperienceFactory, SubTagFactory, TagFactory, StreetActivityFactory
from streetactivity.models import Experience, Tag
from django.urls import reverse
from django.core.exceptions import ValidationError


class TestExperienceModel:
    """Tests for the Experience model."""
    def test_experience_str_method(self):
        """Test the __str__ method of the Experience model to ensure it returns
        the first 50 characters of the report followed by ellipsis."""
        experience = ExperienceFactory(report="This is a test report for the experience model. It should be truncated.")
        expected_str = "This is a test report for the experience model. It..."
        assert str(experience) == expected_str

    def test_experience_str_method_no_report(self):
        """Test the __str__ method of the Experience model when there is no report."""
        activity = StreetActivityFactory(name="Test Activity")
        experience = ExperienceFactory(activity=activity, report="")
        expected_str = f"{activity.name} - Ervaring {experience.id}"
        assert str(experience) == expected_str

    def test_experience_createview_leads_for_form_from_passerby(self, client):
        """Test the Experience create view for passerby to ensure it
        returns a 200 status code and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience-from-passerby", args=[activity.id])
        response = client.get(create_url)
        assert response.status_code == 200
        assert "Ervaring als Voorbijganger" in response.content.decode()

    def test_experience_createview(self, client):
        """Test the Experience create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience", args=[activity.id])

        experience_data = ExperienceFactory.build().__dict__
        for field in ["_state", "id", 'activity_id']:
            experience_data.pop(field, None)

        response = client.post(create_url, experience_data, follow=True)

        assert response.status_code == 200
        assert Experience.objects.count() == 1

    def test_experience_createview_from_practitioner(self, client):
        """Test the Experience create view for practitioners to ensure it
        returns a 200 status code and sets from_practitioner to True."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience-from-practitioner", args=[activity.id])
        experience_data = ExperienceFactory.build().__dict__
        for field in ["_state", "id", 'activity_id']:
            experience_data.pop(field, None)
        response = client.post(create_url, experience_data, follow=True)
        assert response.status_code == 200
        assert Experience.objects.count() == 1
        experience = Experience.objects.first()
        assert experience.from_practitioner

    def test_experience_createview_from_passerby(self, client):
        """Test the Experience create view for passerby to ensure it
        returns a 200 status code and sets from_practitioner to False."""
        activity = StreetActivityFactory()
        create_url = reverse("create-experience-from-passerby", args=[activity.id])
        experience_data = ExperienceFactory.build().__dict__
        for field in ["_state", "id", 'activity_id']:
            experience_data.pop(field, None)
        response = client.post(create_url, experience_data, follow=True)
        assert response.status_code == 200
        assert Experience.objects.count() == 1
        experience = Experience.objects.first()
        assert not experience.from_practitioner

    def test_createview_get_organized_tags(self, client):
        """Test that the Experience create view context contains organized tags."""
        activity = StreetActivityFactory()
        TagFactory.create_batch(2, nvc_category='needs')
        TagFactory.create_batch(2, nvc_category='feelings_fulfilled')
        TagFactory.create_batch(2, nvc_category='feelings_unfulfilled')
        TagFactory.create_batch(2, nvc_category='other')

        create_url = reverse("create-experience", args=[activity.id])
        response = client.get(create_url)

        assert response.status_code == 200
        organized_tags = response.context_data.get("organized_tags_list")
        assert len(organized_tags[0]['main_tags']) == 2
        assert len(organized_tags[1]['main_tags']) == 2
        assert len(organized_tags[2]['main_tags']) == 2
        assert len(organized_tags[3]['main_tags']) == 2

    def test_experience_listview(self, client):
        """Test the Experience list view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()
        for _ in range(3):
            ExperienceFactory(activity=activity)
        response = client.get(reverse("experience-list-streetactivity", args=[activity.id]))
        assert response.status_code == 200
        assert "experiences" in response.context
        assert len(response.context["experiences"]) == 3

    def test_experience_listview_by_streetactivity(self, client):
        """Test the Experience list view filtered by StreetActivity to ensure it
        returns a 200 status code and contains the expected context."""
        activity = StreetActivityFactory()
        ExperienceFactory.create_batch(2, activity=activity)
        ExperienceFactory.create_batch(2)  # Experiences for other activities

        list_url = reverse("experience-list-streetactivity", args=[activity.id])
        response = client.get(list_url)

        assert response.status_code == 200
        assert "experiences" in response.context
        assert len(response.context["experiences"]) == 2
        for experience in response.context["experiences"]:
            assert experience.activity == activity

    def test_experience_listview_by_tag(self, client):
        """Test the Experience list view filtered by Tag to ensure it
        returns a 200 status code and contains the expected context."""
        tag = TagFactory()
        experience_with_tag = ExperienceFactory()
        experience_with_tag.tags.add(tag)

        ExperienceFactory()  # Experience without the tag

        list_url = reverse("experience-list-streetactivity", args=[tag.id])
        response = client.get(list_url)

        assert response.status_code == 200
        assert "experiences" in response.context
        assert len(response.context["experiences"]) == 1
        for experience in response.context["experiences"]:
            assert tag in experience.tags.all()

    def test_experience_ordering(self):
        """Test that Experience instances are ordered by date in descending order."""
        exp1 = ExperienceFactory(date_created="2023-01-01")
        exp2 = ExperienceFactory(date_created="2023-02-01")
        exp3 = ExperienceFactory(date_created="2023-03-01")

        experiences = Experience.objects.all()
        assert list(experiences) == [exp3, exp2, exp1]

    def test_experience_detailview(self, client):
        """Test the Experience detail view to ensure it returns a 200 status code
        and contains the expected context."""
        experience = ExperienceFactory()
        detail_url = reverse("experience-detail", args=[experience.id])

        response = client.get(detail_url)

        assert response.status_code == 200
        assert "experience" in response.context
        assert response.context["experience"].id == experience.id

    def test_experience_short_report_property(self):
        """Test the short_report property of the Experience model."""
        long_report = "This is a long report that exceeds one hundred characters. "* 3
        experience = ExperienceFactory(report=long_report)
        expected_short = long_report[:100] + '...'
        assert experience.short_report == expected_short

    def test_experience_clean_method(self):
        """Test the clean method of the Experience model for validation."""
        experience = ExperienceFactory(report="", external_link="http://example.com")
        try:
            experience.clean()
        except ValidationError as e:
            assert 'report' in e.message_dict
            assert e.message_dict['report'] == ['Vul een verslag in wanneer een externe link wordt toegevoegd.']

    def test_experience_valid_clean_method(self):
        """Test the clean method of the Experience model for valid data."""
        experience = ExperienceFactory(report="This is a valid report.", external_link="http://example.com")
        assert experience.clean() is None

    def test_experience_activity_relationship(self):
        """Test the ForeignKey relationship between Experience and StreetActivity."""
        activity = StreetActivityFactory()
        experience = ExperienceFactory(activity=activity)

        assert experience.activity == activity
        assert experience in activity.experiences.all()

class TestTagModel:
    """Tests for the Tag model."""
    def test_tag_str_method(self):
        """Test the __str__ method of the Tag model to ensure it returns
        the name of the tag."""
        tag = TagFactory(name="Test Tag")
        assert str(tag) == "Test Tag"

    def test_tag_createview(self, client):
        """Test the Tag create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        create_url = reverse("create-tag")

        tag_data = SubTagFactory.build().__dict__
        for field in ["_state", "id" ]:
            tag_data.pop(field, None)

        response = client.post(create_url, tag_data, follow=True)

        assert response.status_code == 200
        assert Tag.objects.count() == 2

    def test_tag_listview(self, client):
        """Test the Tag list view to ensure it returns a 200 status code
        and contains the expected context."""
        TagFactory.create_batch(3)
        response = client.get(reverse("tag-list"))
        assert response.status_code == 200
        assert "tags" in response.context
        assert len(response.context["tags"]) == 3

    def test_tag_listview_context_organization(self, client):
        """Test that the Tag list view context organizes tags by category."""
        needs_tag = TagFactory(nvc_category='needs')
        feelings_fulfilled_tag = TagFactory(nvc_category='feelings_fulfilled')
        feelings_unfulfilled_tag = TagFactory(nvc_category='feelings_unfulfilled')
        other_tag = TagFactory(nvc_category='other')

        response = client.get(reverse("tag-list"))
        context = response.context

        assert needs_tag in context['categories']['needs']['tags']
        assert feelings_fulfilled_tag in context['categories']['feelings_fulfilled']['tags']
        assert feelings_unfulfilled_tag in context['categories']['feelings_unfulfilled']['tags']
        assert other_tag in context['categories']['other']['tags']

    def test_tag_detailview(self, client):
        """Test the Tag detail view to ensure it returns a 200 status code
        and contains the expected context."""
        tag = TagFactory()
        detail_url = reverse("tag-detail", args=[tag.id])

        response = client.get(detail_url)

        assert response.status_code == 200
        assert "tag" in response.context
        assert response.context["tag"].id == tag.id

    def test_tag_hierarchy(self):
        """Test the hierarchical relationship between main tags and subtags."""
        maintag = TagFactory(name="Main Tag")
        subtag1 = TagFactory(name="Sub Tag 1", maintag=maintag)
        subtag2 = TagFactory(name="Sub Tag 2", maintag=maintag)

        assert subtag1.maintag == maintag
        assert subtag2.maintag == maintag
        assert list(maintag.subtags.all()) == [subtag1, subtag2]

    def test_tag_is_maintag_property(self):
        """Test the is_maintag property of the Tag model."""
        maintag = TagFactory(maintag=None)
        subtag = TagFactory(maintag=maintag)

        assert maintag.is_maintag is True
        assert subtag.is_maintag is False
    
    def test_tag_has_subtags_property(self):
        """Test the has_subtags property of the Tag model."""
        maintag = TagFactory(maintag=None)
        subtag = TagFactory(maintag=maintag)

        assert maintag.has_subtags is True
        assert subtag.has_subtags is False

    def test_tag_get_all_related_experiences_method(self):
        """Test the get_all_related_experiences method of the Tag model."""
        maintag = TagFactory()
        subtag = TagFactory(maintag=maintag)

        exp1 = ExperienceFactory()
        exp1.tags.add(maintag)

        exp2 = ExperienceFactory()
        exp2.tags.add(subtag)

        related_experiences = maintag.get_all_related_experiences()

        assert exp1 in related_experiences
        assert exp2 in related_experiences

    def test_tag_get_all_related_experiences_not_maintag(self):
        """Test the get_all_related_experiences method for a tag that is not a main tag."""
        maintag = TagFactory()
        subtag = TagFactory(maintag=maintag)

        exp1 = ExperienceFactory()
        exp1.tags.add(maintag)

        exp2 = ExperienceFactory()
        exp2.tags.add(subtag)

        related_experiences = subtag.get_all_related_experiences()

        assert exp2 in related_experiences
        assert exp1 not in related_experiences

    def test_tag_clean_method(self):
        """Test that the maintag to itself triggers ValidationError in the clean method."""
        tag = TagFactory()
        tag.maintag = tag

        try:
            tag.clean()
        except ValidationError as e:
            assert 'maintag' in e.message_dict
            assert e.message_dict['maintag'] == ['Een tag kan niet zijn eigen hoofdtag zijn.']

    def test_tag_valid_clean_method(self):
        """Test the clean method of the Tag model for valid data."""
        maintag = TagFactory(maintag=None)
        subtag = TagFactory(maintag=maintag)

        assert subtag.clean() is None

    def test_tag_circular_reference_validation(self):
        """Test that circular references in Tag maintag are prevented."""
        maintag = TagFactory(maintag=None)
        subtag = TagFactory(maintag=maintag)

        maintag.maintag = subtag

        try:
            maintag.clean()
        except ValidationError as e:
            assert 'maintag' in e.message_dict
            assert e.message_dict['maintag'] == ['Alleen tags zonder hoofdtag kunnen als hoofdtag worden geselecteerd']
