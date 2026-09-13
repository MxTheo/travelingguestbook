from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from streetactivity.models import Reflection
from travelingguestbook.factories import ReflectionFactory


class TestFetchMastodonPostsCommand:
    """Tests for the fetch_mastodon_posts management command."""
    @patch("streetactivity.management.commands.fetch_mastodon_posts.fetch_mastodon_posts")
    def test_success(self, mock_fetch):
        """
        Test if the management command calls the service and outputs the correct result.
        """
        mock_fetch.return_value = 2

        out = StringIO()
        call_command("fetch_mastodon_posts", stdout=out)

        assert "Succesvol 2 nieuwe reflecties opgehaald en opgeslagen!" in out.getvalue()

        mock_fetch.assert_called_once_with("#bedanktvoorhetcontact")

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_with_latest_reflection(self, mock_fetch):
        """
        Test that since_id is correctly used when a latest_reflection exists.

        This ensures that the function only fetches new posts since the last fetched reflection.
        """
        ReflectionFactory(
            external_id="67890",
            platform="mastodon",
        )

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "11111",
                "content": "<p>New post</p>",
                "account": {
                    "username": "newuser",
                    "url": "https://newuser.com",
                },
                "url": "https://test.com/post/2",
                "created_at": "2023-01-01T12:00:00.000Z",
                "media_attachments": [],
                "tags": [{"name": "test"}],
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_fetch.return_value = mock_response

        out = StringIO()
        call_command("fetch_mastodon_posts", stdout=out)

        mock_fetch.assert_called_once()
        called_params = mock_fetch.call_args.kwargs["params"]
        assert "since_id" in called_params
        assert called_params["since_id"] == "67890"

        assert Reflection.objects.filter(external_id="11111").exists()
        assert "1" in out.getvalue()


    @patch("streetactivity.management.commands.fetch_mastodon_posts.fetch_mastodon_posts")
    def test_failure(self, mock_fetch):
        """
        Test if the management command handles errors in the service correctly.
        """
        mock_fetch.side_effect = Exception("Service failed")

        out = StringIO()
        with pytest.raises(Exception, match="Service failed"):
            call_command("fetch_mastodon_posts", stdout=out)

        mock_fetch.assert_called_once_with("#bedanktvoorhetcontact")
