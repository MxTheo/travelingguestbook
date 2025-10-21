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

    def test_experience_listview(self, client):
        """Test the Experience list view to ensure it returns a 200 status code
        and contains the expected context."""
        ExperienceFactory.create_batch(3)
        response = client.get(reverse("experience-list"))
        assert response.status_code == 200
        assert "experiences" in response.context
        assert len(response.context["experiences"]) == 3

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
        main_tag = TagFactory(name="Main Tag")
        sub_tag1 = TagFactory(name="Sub Tag 1", main_tag=main_tag)
        sub_tag2 = TagFactory(name="Sub Tag 2", main_tag=main_tag)

        assert sub_tag1.main_tag == main_tag
        assert sub_tag2.main_tag == main_tag
        assert list(main_tag.sub_tags.all()) == [sub_tag1, sub_tag2]

    def test_tag_is_main_tag_property(self):
        """Test the is_main_tag property of the Tag model."""
        main_tag = TagFactory(main_tag=None)
        sub_tag = TagFactory(main_tag=main_tag)

        assert main_tag.is_main_tag is True
        assert sub_tag.is_main_tag is False
    
    def test_tag_has_subtags_property(self):
        """Test the has_subtags property of the Tag model."""
        main_tag = TagFactory(main_tag=None)
        sub_tag = TagFactory(main_tag=main_tag)

        assert main_tag.has_subtags is True
        assert sub_tag.has_subtags is False

    def test_tag_get_all_related_experiences_method(self):
        """Test the get_all_related_experiences method of the Tag model."""
        main_tag = TagFactory()
        sub_tag = TagFactory(main_tag=main_tag)

        exp1 = ExperienceFactory()
        exp1.tags.add(main_tag)

        exp2 = ExperienceFactory()
        exp2.tags.add(sub_tag)

        related_experiences = main_tag.get_all_related_experiences()

        assert exp1 in related_experiences
        assert exp2 in related_experiences

    def test_tag_get_all_related_experiences_not_main_tag(self):
        """Test the get_all_related_experiences method for a tag that is not a main tag."""
        main_tag = TagFactory()
        sub_tag = TagFactory(main_tag=main_tag)

        exp1 = ExperienceFactory()
        exp1.tags.add(main_tag)

        exp2 = ExperienceFactory()
        exp2.tags.add(sub_tag)

        related_experiences = sub_tag.get_all_related_experiences()

        assert exp2 in related_experiences
        assert exp1 not in related_experiences

    def test_tag_clean_method(self):
        """Test that the main_tag to itself triggers ValidationError in the clean method."""
        tag = TagFactory()
        tag.main_tag = tag

        try:
            tag.clean()
        except ValidationError as e:
            assert 'main_tag' in e.message_dict
            assert e.message_dict['main_tag'] == ['Een tag kan niet zijn eigen hoofdtag zijn.']

    def test_tag_valid_clean_method(self):
        """Test the clean method of the Tag model for valid data."""
        main_tag = TagFactory(main_tag=None)
        sub_tag = TagFactory(main_tag=main_tag)

        assert sub_tag.clean() is None

    def test_tag_circular_reference_validation(self):
        """Test that circular references in Tag main_tag are prevented."""
        main_tag = TagFactory(main_tag=None)
        sub_tag = TagFactory(main_tag=main_tag)

        main_tag.main_tag = sub_tag

        try:
            main_tag.clean()
        except ValidationError as e:
            assert 'main_tag' in e.message_dict
            assert e.message_dict['main_tag'] == ['Alleen tags zonder hoofdtag kunnen als hoofdtag worden geselecteerd.']


