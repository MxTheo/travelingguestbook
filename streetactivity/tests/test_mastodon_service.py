from unittest.mock import MagicMock, patch

import requests
from django.conf import settings

from streetactivity.models import Reflection
from streetactivity.services.mastodon_service import fetch_mastodon_posts
from streetactivity.templatetags.markdown_tags import markdown_to_html


class TestFetchMastodonPosts:
    """Tests for the fetch_mastodon_posts function in the mastodon_service module."""
    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_fetch_mastodon_posts_success(self, mock_get, settings):
        """
        Test if the Mastodon API is called successfully and posts are saved.
        """
        # Set Mastodon server and token
        settings.MASTODON_SERVER = "mastodon.test"
        settings.MASTODON_ACCESS_TOKEN = "test_token"

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "12345",
                "content": "This is a test reflection!",
                "account": {
                    "username": "testuser",
                    "url": "https://mastodon.test/@testuser",
                },
                "url": "https://mastodon.test/@testuser/12345",
                "created_at": "2026-09-10T12:00:00.000Z",
                "media_attachments": [],
                "tags": [{"name": "testhashtag"}],
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the function
        count = fetch_mastodon_posts("#testhashtag")

        # Assert the function retrieved the correct number of posts
        assert count == 1

        # Assert the post is saved in the database
        reflection = Reflection.objects.first()
        assert reflection is not None
        assert reflection.reflection == "This is a test reflection!\n\n"
        assert reflection.platform == "mastodon"
        assert reflection.author_username == "testuser"
        assert reflection.post_url == "https://mastodon.test/@testuser/12345"
        assert reflection.hashtags == ["testhashtag"]

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_fetch_mastodon_posts_failure(self, mock_get, settings):
        """
        Test if the function handles API errors correctly.
        """
        # Set Mastodon server and token
        settings.MASTODON_SERVER = "mastodon.test"
        settings.MASTODON_ACCESS_TOKEN = "test_token"

        # Mock a RequestException (de juiste exception voor requests)
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        # Call the function
        count = fetch_mastodon_posts("#testhashtag")

        # Assert the function returns 0
        assert count == 0

class TestMarkdownToHtml:
    """Tests for the markdown_to_html function in the mastodon_service module."""
    def test_markdown_to_html(self):
        """
        Test if the markdown_to_html function converts markdown to HTML correctly.
        """

        markdown_text = "**Bold Text** and *Italic Text*"
        expected_html = "<p><strong>Bold Text</strong> and <em>Italic Text</em></p>"
        assert markdown_to_html(markdown_text) == expected_html