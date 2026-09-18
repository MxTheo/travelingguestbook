"""Tests for the Bluesky service.

Verifies that ``fetch_bluesky_posts`` correctly fetches, normalizes and
returns Bluesky posts as a list of dictionaries, without persisting
anything itself. Also covers the private helpers that extract hashtags,
media URLs and permalinks.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests

from streetactivity.models import Reflection
from streetactivity.services.bluesky_service import (
    _build_post_url,
    _extract_hashtags,
    _extract_media_url,
    fetch_bluesky_posts,
)
from travelingguestbook.factories import ReflectionFactory


def _bluesky_post(
    uri="at://did:plc:abc/app.bsky.feed.post/1",
    created_at="2026-01-01T12:00:00.000Z",
    text="Test #bvhc",
):
    """Build a minimal Bluesky search-posts payload.

    Args:
        uri: The AT-URI identifying the post.
        created_at: ISO-8601 timestamp string from the Bluesky API.
        text: The raw post text.

    Returns:
        A dict mimicking a single item from the Bluesky search endpoint.
    """
    return {
        "uri": uri,
        "record": {"text": text, "createdAt": created_at, "facets": []},
        "author": {"handle": "tester.bsky.social"},
    }


@pytest.mark.django_db
class TestFetchBlueskyPosts:
    """Tests for the ``fetch_bluesky_posts`` service function.

    Covers normalization, ``since`` optimization and error handling.
    Each test mocks ``requests.get`` so no real network calls are made.
    """

    @patch("streetactivity.services.bluesky_service.requests.get")
    def test_returns_normalized_dicts(self, mock_get):
        """The service returns a list of normalized dicts and saves nothing."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"posts": [_bluesky_post()]}
        mock_get.return_value = mock_response

        result = fetch_bluesky_posts("#bvhc")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["external_id"] == "at://did:plc:abc/app.bsky.feed.post/1"
        assert result[0]["author_username"] == "tester.bsky.social"
        # Service must not save anything itself
        assert Reflection.objects.count() == 0

    @patch("streetactivity.services.bluesky_service.requests.get")
    def test_since_is_added_when_existing_posts(self, mock_get):
        """The timestamp of the most recent stored post is passed as ``since``."""
        existing_ts = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        ReflectionFactory(
            platform="bluesky",
            external_id="at://did:plc:old/app.bsky.feed.post/old",
            timestamp=existing_ts,
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"posts": []}
        mock_get.return_value = mock_response

        fetch_bluesky_posts("#bvhc")

        _, kwargs = mock_get.call_args
        assert kwargs["params"]["since"] == existing_ts.isoformat()

    @patch("streetactivity.services.bluesky_service.requests.get")
    def test_no_since_when_no_existing_posts(self, mock_get):
        """No ``since`` parameter is sent when the database has no posts."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"posts": []}
        mock_get.return_value = mock_response

        fetch_bluesky_posts("#bvhc")

        _, kwargs = mock_get.call_args
        assert "since" not in kwargs["params"]

    @patch("streetactivity.services.bluesky_service.logger")
    @patch("streetactivity.services.bluesky_service.requests.get")
    def test_request_exception_returns_empty_list(self, mock_get, mock_logger):
        """A ``RequestException`` is logged and results in an empty list."""
        mock_get.side_effect = requests.RequestException("boom")

        result = fetch_bluesky_posts("#bvhc")

        assert not result
        mock_logger.error.assert_called_once()
        assert "Bluesky API request failed" in mock_logger.error.call_args[0][0]


class TestExtractHashtags:
    """Tests for the ``_extract_hashtags`` helper."""

    def test_extracts_tags_from_facets(self):
        """Only facet features of type ``facet#tag`` are extracted."""
        post = {
            "record": {
                "facets": [
                    {"features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "bvhc"}]},
                    {"features": [{"$type": "app.bsky.richtext.facet#mention", "did": "x"}]},
                ]
            }
        }
        assert _extract_hashtags(post) == ["#bvhc"]

    def test_returns_empty_list_when_no_facets(self):
        """A post without facets yields an empty hashtag list."""
        assert not _extract_hashtags({})


class TestExtractMediaUrl:
    """Tests for the ``_extract_media_url`` helper."""

    def test_returns_none_when_no_embed(self):
        """A post without an embed has no media URL."""
        assert _extract_media_url({}) is None

    def test_returns_none_when_embed_has_no_images(self):
        """An embed without images yields ``None``."""
        assert _extract_media_url({"embed": {"$type": "app.bsky.embed.external"}}) is None

    def test_returns_none_when_images_empty(self):
        """An empty images list yields ``None``."""
        assert _extract_media_url({"embed": {"images": []}}) is None

    def test_returns_url_when_image_present(self):
        """The ``fullsize`` URL of the first image is returned."""
        post = {"embed": {"images": [{"fullsize": "https://cdn.bsky.app/x.jpg"}]}}
        assert _extract_media_url(post) == "https://cdn.bsky.app/x.jpg"


class TestBuildPostUrl:
    """Tests for the ``_build_post_url`` helper."""

    def test_returns_empty_string_for_short_uri(self):
        """An AT-URI with fewer than 5 parts yields an empty string."""
        assert _build_post_url({"uri": "at://did:plc:abc"}) == ""

    def test_returns_empty_string_for_empty_uri(self):
        """A post without a ``uri`` yields an empty string."""
        assert _build_post_url({}) == ""

    def test_returns_bsky_url_for_valid_uri(self):
        """A valid AT-URI is converted to a bsky.app permalink."""
        post = {"uri": "at://did:plc:abc/app.bsky.feed.post/rkey1"}
        assert _build_post_url(post) == "https://bsky.app/profile/did:plc:abc/post/rkey1"
