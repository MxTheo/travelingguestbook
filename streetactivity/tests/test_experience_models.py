from travelingguestbook.factories import ExperienceFactory, TagFactory

class TestExperienceModel:
    """Tests for the Experience model."""
    def test_experience_str_method(self):
        """Test the __str__ method of the Experience model to ensure it returns
        the first 50 characters of the report followed by ellipsis."""
        experience = ExperienceFactory(report="This is a test report for the experience model. It should be truncated.")
        expected_str = "This is a test report for the experience model. It..."
        assert str(experience) == expected_str


class TestTagModel:
    """Tests for the Tag model."""
    def test_tag_str_method(self):
        """Test the __str__ method of the Tag model to ensure it returns
        the name of the tag."""
        tag = TagFactory(name="Test Tag")
        assert str(tag) == "Test Tag"