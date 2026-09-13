from django.core.management.base import BaseCommand

from streetactivity.services.mastodon_service import fetch_mastodon_posts


class Command(BaseCommand):
    """Django management command to fetch Mastodon posts with a specific hashtag
    and save them as Reflection objects."""
    help = """Haalt posts met de hashtag #bedanktvoorhetcontact op van Mastodon
    en slaat ze op in de database."""

    def handle(self, *args, **options):
        count = fetch_mastodon_posts("#bedanktvoorhetcontact")
        self.stdout.write(self.style.SUCCESS(
            f"Succesvol {count} nieuwe reflecties opgehaald en opgeslagen!"
            ))
