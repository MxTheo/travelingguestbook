import pytest
from faker import Faker
from travelingguestbook.factories import StreetActivityFactory, SWOTElementFactory
from streetactivity.models import SWOTElement

fake = Faker()
Faker.seed(0)


class TestSWOTElementModel:
    """Test cases for SWOTElement model"""

    def test_swot_element_creation(self):
        """Test that SWOT element can be created with required fields"""
        activity = StreetActivityFactory()
        element = SWOTElementFactory(
            street_activity=activity,
            element_type='W',
            formulation="Test formulation"
        )

        assert element.street_activity == activity
        assert element.element_type == 'W'
        assert element.formulation == "Test formulation"
        assert element.recognition_count == 0
        assert element.needs_voting is False

    def test_swot_element_string_representation(self):
        """Test the string representation of SWOT element"""
        element = SWOTElementFactory(
            element_type='S',
            formulation="Strong community engagement"
        )

        assert "S: Strong community engagement" in str(element)

    def test_swot_element_default_ordering(self):
        """Test that elements are ordered by recognition count and creation date"""
        activity = StreetActivityFactory()

        # Create elements with different recognition counts
        SWOTElementFactory(
            street_activity=activity,
            recognition_count=2,
            element_type='W'
        )
        element_high = SWOTElementFactory(
            street_activity=activity,
            recognition_count=5,
            element_type='W'
        )
        element_recent = SWOTElementFactory(
            street_activity=activity,
            recognition_count=2,
            element_type='W'
        )

        elements = SWOTElement.objects.all()
        assert elements[0] == element_high  # Highest recognition first
        assert elements[1] == element_recent  # Most recent of same count

    def test_swot_element_alternative_formulation(self):
        """Test alternative formulation field"""
        element = SWOTElementFactory(
            formulation="Original text",
            alternative_formulation="Alternative text",
            needs_voting=True
        )
        
        assert element.alternative_formulation == "Alternative text"
        assert element.needs_voting is True
    
    def test_vote_counts_default_to_zero(self):
        """Test that vote counts default to zero"""
        element = SWOTElementFactory()
        
        assert element.votes_current == 0
        assert element.votes_alternative == 0
    
    @pytest.mark.parametrize("element_type,expected_display", [
        ('S', 'Sterke punt'),
        ('W', 'Zwakke punt'),
        ('O', 'Kans'),
        ('T', 'Bedreiging'),
    ])
    def test_element_type_choices(self, element_type, expected_display):
        """Test all SWOT element type choices"""
        element = SWOTElementFactory(element_type=element_type)
        
        assert element.get_element_type_display() == expected_display