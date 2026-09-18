"""Tests for the Mastodon service.

Verifies that ``fetch_mastodon_posts`` correctly fetches, normalizes and
returns Mastodon posts as a list of dictionaries, without persisting
anything itself. Persistence is the responsibility of the management
command.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import requests

from streetactivity.models import Reflection
from streetactivity.services.mastodon_service import fetch_mastodon_posts
from streetactivity.templatetags.markdown_tags import markdown_to_html
from travelingguestbook.factories import ReflectionFactory


def _mastodon_post(post_id, created_at="2026-01-01T12:00:00.000Z"):
    """Build a minimal Mastodon API post payload.

    Args:
        post_id: The Mastodon post ID (string).
        created_at: ISO-8601 timestamp string in Mastodon's format.

    Returns:
        A dict mimicking a single item from the Mastodon timeline endpoint.
    """
    return {
        "id": post_id,
        "content": f"<p>Post {post_id}</p>",
        "account": {"username": f"user{post_id}", "url": f"https://m/@user{post_id}"},
        "url": f"https://m/@user{post_id}/{post_id}",
        "created_at": created_at,
        "media_attachments": [],
        "tags": [{"name": "bvhc"}],
    }


class TestFetchMastodonPosts:
    """Tests for the ``fetch_mastodon_posts`` service function.

    Covers normalization, ``since_id`` optimization, error handling and
    media URL extraction. Each test mocks ``requests.get`` so no real
    network calls are made.
    """

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_returns_normalized_dicts(self, mock_get):
        """The service returns a list of normalized dicts and saves nothing."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [_mastodon_post("100")]
        mock_get.return_value = mock_response

        result = fetch_mastodon_posts("#bvhc")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["external_id"] == "100"
        assert result[0]["author_username"] == "user100"
        # Service must not save anything itself
        assert Reflection.objects.count() == 0

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_uses_since_id_when_existing_posts(self, mock_get):
        """The most recent stored Mastodon ID is passed as ``since_id``."""
        ReflectionFactory(
            platform="mastodon",
            external_id="42",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        fetch_mastodon_posts("#bvhc")

        _, kwargs = mock_get.call_args
        assert kwargs["params"]["since_id"] == "42"

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_no_since_id_when_no_existing_posts(self, mock_get):
        """No ``since_id`` is sent when the database has no Mastodon posts."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        fetch_mastodon_posts("#bvhc")

        _, kwargs = mock_get.call_args
        assert kwargs["params"] == {}

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_request_exception_returns_empty_list(self, mock_get, capsys):
        """A ``RequestException`` is caught and results in an empty list."""
        mock_get.side_effect = requests.RequestException("boom")

        result = fetch_mastodon_posts("#bvhc")

        assert not result
        out = capsys.readouterr().out
        assert "Error fetching Mastodon posts" in out

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_media_url_when_attachments_present(self, mock_get):
        """The first media attachment URL is extracted."""
        post = _mastodon_post("200")
        post["media_attachments"] = [{"url": "https://cdn.m/img.jpg"}]

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [post]
        mock_get.return_value = mock_response

        result = fetch_mastodon_posts("#bvhc")

        assert result[0]["media_url"] == "https://cdn.m/img.jpg"

    @patch("streetactivity.services.mastodon_service.requests.get")
    def test_media_url_none_when_no_attachments(self, mock_get):
        """``media_url`` is ``None`` when a post has no attachments."""
        post = _mastodon_post("300")
        post["media_attachments"] = []

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [post]
        mock_get.return_value = mock_response

        result = fetch_mastodon_posts("#bvhc")

        assert result[0]["media_url"] is None

class TestMarkdownToHtml:
    """Tests for the markdown_to_html function in the mastodon_service module."""
    def test_markdown_to_html(self):
        """
        Test if the markdown_to_html function converts markdown to HTML correctly.
        """

        markdown_text = "**Bold Text** and *Italic Text*"
        expected_html = "<p><strong>Bold Text</strong> and <em>Italic Text</em></p>"
        assert markdown_to_html(markdown_text) == expected_html
