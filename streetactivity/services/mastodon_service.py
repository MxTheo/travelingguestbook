from datetime import datetime, timezone

import html2text
import requests
from django.conf import settings

from streetactivity.models import Reflection


def fetch_mastodon_posts(hashtag="#bedanktvoorhetcontact") -> list[dict]:
    """
    Fetch posts with the specified hashtag from Mastodon.

    Returns a list of normalized post dictionaries suitable for
    creating Reflection objects.
    """
    url = f"https://{settings.MASTODON_SERVER}/api/v1/timelines/tag/{hashtag.lstrip('#')}"
    headers = {"Authorization": f"Bearer {settings.MASTODON_ACCESS_TOKEN}"}

    latest_reflection = Reflection.objects.filter(
        platform="mastodon",
        external_id__isnull=False,
    ).order_by("-timestamp").first()

    params = {"since_id": latest_reflection.external_id} if latest_reflection else {}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        posts = response.json()
    except requests.RequestException as exc:
        print(f"Error fetching Mastodon posts: {exc}")
        return []

    h = html2text.HTML2Text()
    normalized = []

    for post in posts:
        normalized.append({
            "external_id": post["id"],
            "reflection": h.handle(post.get("content", "")),
            "author_username": post["account"]["username"],
            "author_profile_url": post["account"]["url"],
            "post_url": post["url"],
            "timestamp": datetime.strptime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).replace(tzinfo=timezone.utc),
            "media_url": (
                post.get("media_attachments", [{}])[0].get("url")
                if post.get("media_attachments") else None
            ),
            "hashtags": [tag["name"] for tag in post.get("tags", [])],
        })

    return normalized
