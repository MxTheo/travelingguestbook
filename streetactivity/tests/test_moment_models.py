from django.urls import reverse
from travelingguestbook.factories import WordFactory, StreetActivityFactory
from streetactivity.models import Word

class TestWordModel:
    """Tests for the Word model."""
    def test_word_str_method(self):
        """Test the __str__ method of the Word model returns the word"""
        expected_str = "Test123"
        word = WordFactory(
            word=expected_str)
        returned_str = str(word)
        assert returned_str == expected_str

    def test_word_str_method_no_word(self):
        """Test the __str__ method of the Word model when there is no word."""
        activity = StreetActivityFactory(name="Test Activity")
        word = WordFactory(activity=activity, word="")
        assert str(word) == ""

    def test_word_createview(self, auto_login_user):
        """Test the Word create view to ensure it returns a 200 status code
        and contains the expected form in context."""
        client, _ = auto_login_user()
        activity = StreetActivityFactory()
        create_url = reverse("create-word", args=[activity.id])

        word_data = create_word_data(activity)

        response = client.post(create_url, word_data, follow=True)

        assert response.status_code == 200
        assert Word.objects.count() == 1

    def test_word_createview_user_assignment(self, auto_login_user):
        """Test that the user is correctly assigned to the Word when created."""
        client, user = auto_login_user()
        activity = StreetActivityFactory()
        create_url = reverse("create-word", args=[activity.id])
        word_data = create_word_data(activity)
        response = client.post(create_url, word_data, follow=True)
        assert response.status_code == 200
        word = Word.objects.first()
        assert word.user == user

    def test_word_listview(self, client):
        """Test the Word list view to ensure it returns a 200 status code
        and contains the expected context."""
        activity = StreetActivityFactory()
        for _ in range(3):
            WordFactory(activity=activity)
        response = client.get(reverse("word-list-streetactivity", args=[activity.id]))
        assert response.status_code == 200
        assert "words" in response.context
        assert len(response.context["words"]) == 3

    def test_word_listview_by_streetactivity(self, client):
        """Test the Word list view filtered by StreetActivity to ensure it
        returns a 200 status code and contains the expected context."""
        activity = StreetActivityFactory()
        WordFactory.create_batch(2, activity=activity)
        WordFactory.create_batch(2)  # Words for other activities

        list_url = reverse("word-list-streetactivity", args=[activity.id])
        response = client.get(list_url)

        assert response.status_code == 200
        assert "words" in response.context
        assert len(response.context["words"]) == 2
        for word in response.context["words"]:
            assert word.activity == activity

    def test_word_ordering(self):
        """Test that Word instances are ordered by date in descending order."""
        exp1 = WordFactory(date_created="2023-01-01")
        exp2 = WordFactory(date_created="2023-02-01")
        exp3 = WordFactory(date_created="2023-03-01")

        words = Word.objects.all()
        assert list(words) == [exp3, exp2, exp1]

    def test_word_activity_relationship(self):
        """Test the ForeignKey relationship between Word and StreetActivity."""
        activity = StreetActivityFactory()
        word = WordFactory(activity=activity)

        assert word.activity == activity
        assert word in activity.words.all()

    def test_delete_view(self, client):
        """Test the Word delete view to ensure it returns a 200 status code
        and contains the expected context."""
        word = WordFactory()

        delete_word_url = reverse("delete-word", args=[word.id])

        response = client.post(delete_word_url)

        assert response.status_code == 302
        assert not Word.objects.filter(id=word.id).exists()
        assert Word.objects.count() == 0

    def test_update_view(self, client):
        """Test the Word update view to ensure it returns a 200 status code
        and contains the expected form in context."""
        word = WordFactory()
        update_url = reverse("update-word", args=[word.id])

        updated_data = {
            "word": "Updated",
            "activity": word.activity,
        }

        response = client.post(update_url, updated_data, follow=True)

        assert response.status_code == 200

        word.refresh_from_db()
        assert word.word == "Updated"

    def test_get_context_data_word_createview(self, client):
        """Given the user creates a word,
        test if activity is in the context"""
        activity = StreetActivityFactory()
        create_url = reverse("create-word", args=[activity.id])
        response = client.get(create_url)
        assert response.status_code == 200
        assert "activity" in response.context

    def test_get_context_data_word_updateview(self,client):
        """Given the user updates a word,
        test if activity is in the context"""
        word = WordFactory()
        update_url = reverse("update-word", args=[word.id])
        response = client.get(update_url)
        assert response.status_code == 200
        assert "activity" in response.context

    def test_word_missing_on_word_form(self, client):
        """Given the user forgets to fill in a word,
        test if the error 'Geen woord gegeven' is given"""
        activity = StreetActivityFactory()
        create_url = reverse("create-word", args=[activity.id])
        word_data = create_word_data(activity)
        word_data.pop("word", None)

        response = client.post(create_url, word_data)

        assert response.status_code == 200
        assert "Geen woord gegeven" in response.content.decode()


def create_word_data(activity=None):
    """Helper function to create word data for tests."""
    word_data = WordFactory.build().__dict__
    for field in [
        "_state",
        "id",
        'activity_id',
        'user_id',
        'date_created', 'date_modified']:
        word_data.pop(field, None)
    word_data['activity'] = activity.id
    return word_data
