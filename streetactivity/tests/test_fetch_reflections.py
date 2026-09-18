"""Tests for the ``fetch_reflections`` management command.

Verifies that the command orchestrates the Mastodon and Bluesky services
and persists their results as ``Reflection`` objects, using
``get_or_create`` on ``(external_id, platform)`` to avoid duplicates.
"""

from unittest.mock import patch

from django.core.management import call_command

from streetactivity.management.commands.fetch_reflections import Command
from streetactivity.models import Reflection


class TestFetchReflectionsCommand:
    """Tests for the ``handle`` method of the command.

    Both services are mocked, so these tests exercise only the
    orchestration and output logic of the command.
    """

    @patch("streetactivity.management.commands.fetch_reflections.fetch_bluesky_posts")
    @patch("streetactivity.management.commands.fetch_reflections.fetch_mastodon_posts")
    def test_handle_saves_posts_from_both_services(
        self, mock_mastodon, mock_bluesky, capsys
    ):
        """Posts returned by both services are persisted with correct platform."""
        mock_mastodon.return_value = [{
            "external_id": "m-1",
            "reflection": "Mastodon post",
            "author_username": "m_user",
            "post_url": "https://mastodon/@m_user/1",
        }]
        mock_bluesky.return_value = [{
            "external_id": "at://b-1",
            "reflection": "Bluesky post",
            "author_username": "b_user",
            "post_url": "https://bsky.app/profile/b_user/post/1",
        }]

        call_command("fetch_reflections")

        assert Reflection.objects.filter(platform="Mastodon").count() == 1
        assert Reflection.objects.filter(platform="Bluesky").count() == 1
        out = capsys.readouterr().out
        assert "1" in out

    @patch("streetactivity.management.commands.fetch_reflections.fetch_bluesky_posts",
           return_value=[])
    @patch("streetactivity.management.commands.fetch_reflections.fetch_mastodon_posts",
           return_value=[])
    def test_handle_with_zero_results(self, mock_mastodon, mock_bluesky, capsys):
        """An empty result from both services saves nothing and reports zero."""
        call_command("fetch_reflections")

        assert Reflection.objects.count() == 0
        out = capsys.readouterr().out
        assert "0" in out

    @patch("streetactivity.management.commands.fetch_reflections.fetch_bluesky_posts",
           return_value=[])
    @patch("streetactivity.management.commands.fetch_reflections.fetch_mastodon_posts",
           return_value=[])
    def test_handle_calls_services_with_correct_hashtags(
        self, mock_mastodon, mock_bluesky
    ):
        """Each service is called with its platform-specific hashtag."""
        call_command("fetch_reflections")

        mock_mastodon.assert_called_once_with("#bedanktvoorhetcontact")
        mock_bluesky.assert_called_once_with("#bvhc")


class TestSaveReflections:
    """Tests for the ``_save_reflections`` helper on the command.

    Verifies deduplication on ``(external_id, platform)``, handling of
    missing external IDs, and the correct return count of newly created
    rows.
    """

    def _post(self, external_id):
        """Build a minimal normalized post dict for testing.

        Args:
            external_id: The external ID value; may be ``None`` or ``""``.

        Returns:
            A dict with the fields expected by ``_save_reflections``.
        """
        return {
            "external_id": external_id,
            "reflection": "text",
            "author_username": "x",
            "post_url": "https://example.com/1",
        }

    def test_skips_post_without_external_id(self):
        """Posts with a falsy ``external_id`` are skipped entirely."""
        cmd = Command()
        count = cmd._save_reflections(
            [self._post(None), self._post("")], platform="Bluesky"
        )

        assert count == 0
        assert Reflection.objects.count() == 0

    def test_saves_post_with_external_id(self):
        """A post with an ``external_id`` is saved and counted."""
        cmd = Command()
        count = cmd._save_reflections([self._post("at://x/1")], platform="Bluesky")

        assert count == 1
        assert Reflection.objects.count() == 1

    def test_duplicate_is_skipped(self):
        """Saving the same ``(external_id, platform)`` twice creates one row."""
        cmd = Command()
        post = self._post("at://x/1")

        cmd._save_reflections([post], platform="Bluesky")
        count = cmd._save_reflections([post], platform="Bluesky")

        assert count == 0
        assert Reflection.objects.count() == 1

    def test_same_external_id_different_platform_is_saved(self):
        """Identical external IDs on different platforms are distinct rows."""
        cmd = Command()
        post = self._post("shared-id")

        cmd._save_reflections([post], platform="Bluesky")
        cmd._save_reflections([post], platform="Mastodon")

        assert Reflection.objects.count() == 2
