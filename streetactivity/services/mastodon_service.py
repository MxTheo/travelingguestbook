from datetime import datetime, timezone

import html2text
import requests
from django.conf import settings

from streetactivity.models import Reflection


def fetch_mastodon_posts(hashtag="#bedanktvoorhetcontact"):
    """
    Fetches posts with the specified hashtag from Mastodon and saves them as Reflection objects.
    Returns the number of reflections fetched.
    """
    # Mastodon API endpoint to fetch posts with a hashtag
    url = f"https://{settings.MASTODON_SERVER}/api/v1/timelines/tag/{hashtag.lstrip('#')}"

    headers = {
        "Authorization": f"Bearer {settings.MASTODON_ACCESS_TOKEN}"
    }

    latest_reflection = Reflection.objects.filter(
        platform="mastodon",
        external_id__isnull=False
    ).order_by("-timestamp").first()

    if latest_reflection:
        since_id = latest_reflection.external_id
        params = {"since_id": since_id}
    else:
        params = {}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raises an exception for HTTP errors
        posts = response.json()

        h = html2text.HTML2Text()

        reflections = []
        for post in posts:
            if not Reflection.objects.filter(external_id=post["id"]).exists():
                reflection = Reflection(
                    external_id=post["id"],
                    reflection=h.handle(post.get("content", "")),
                    platform="mastodon",
                    author_username=post["account"]["username"],
                    author_profile_url=post["account"]["url"],
                    post_url=post["url"],
                    timestamp=datetime.strptime(post["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc),
                    media_url=post.get("media_attachments", [{}]).get("url") if post.get("media_attachments") else None,
                    hashtags=[tag["name"] for tag in post.get("tags", [])],
                )
                reflections.append(reflection)

        Reflection.objects.bulk_create(reflections, ignore_conflicts=True)

        return len(reflections)

    except requests.exceptions.RequestException as e:
        # Log the error (optional)
        print(f"Error fetching Mastodon posts: {e}")
        # Return 0 to indicate no reflections were fetched
        return 0
