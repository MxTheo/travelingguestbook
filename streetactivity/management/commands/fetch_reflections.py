from django.core.management.base import BaseCommand

from streetactivity.models import Reflection
from streetactivity.services.bluesky_service import fetch_bluesky_posts
from streetactivity.services.mastodon_service import fetch_mastodon_posts


class Command(BaseCommand):
    """
    Fetch posts with #bedanktvoorhetcontact from Mastodon and Bluesky
    and store them as Reflection objects.
    """
    help = "Fetch Mastodon and Bluesky posts with #bedanktvoorhetcontact and save as reflections."

    def handle(self, *args, **options):
        mastodon_count = self._save_reflections(
            fetch_mastodon_posts("#bedanktvoorhetcontact"),
            platform="Mastodon",
        )
        bluesky_count = self._save_reflections(
            fetch_bluesky_posts("#bvhc"),
            platform="Bluesky",
        )

        self.stdout.write(self.style.SUCCESS(
            f"Mastodon: {mastodon_count} new reflections, "
            f"Bluesky: {bluesky_count} new reflections saved."
        ))

    def _save_reflections(self, posts: list[dict], platform: str) -> int:
        """Persist normalized post dicts, skipping duplicates."""
        created = 0
        for post in posts:
            external_id = post.get("external_id")
            if not external_id:
                continue

            _, is_new = Reflection.objects.get_or_create(
                external_id=external_id,
                platform=platform,
                defaults={
                    "reflection": post.get("reflection", "")[:1000],
                    "author_username": post.get("author_username"),
                    "author_profile_url": post.get("author_profile_url"),
                    "post_url": post.get("post_url"),
                    "timestamp": post.get("timestamp"),
                    "media_url": post.get("media_url"),
                    "hashtags": post.get("hashtags", []),
                },
            )
            if is_new:
                created += 1

        return created
