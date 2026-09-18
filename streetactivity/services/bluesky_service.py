import logging

import requests
from django.utils.dateparse import parse_datetime

from streetactivity.models import Reflection

logger = logging.getLogger(__name__)

BLUESKY_SEARCH_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"


def fetch_bluesky_posts(hashtag: str, limit: int = 100) -> list[dict]:
    """
    Fetch public Bluesky posts for a given hashtag.

    Returns a list of normalized post dictionaries suitable for
    creating Reflection objects.
    """
    latest = (
        Reflection.objects.filter(platform="bluesky", external_id__isnull=False)
        .order_by("-timestamp")
        .first()
    )

    params = {"q": hashtag, "tag": hashtag.lstrip("#"), "limit": limit}
    if latest and latest.timestamp:
        params["since"] = latest.timestamp.isoformat()

    try:
        response = requests.get(BLUESKY_SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Bluesky API request failed: %s", exc)
        return []

    payload = response.json()
    posts = payload.get("posts", [])
    normalized = []

    for post in posts:
        record = post.get("record", {})
        author = post.get("author", {})

        normalized.append({
            "external_id": post.get("uri"),
            "reflection": record.get("text", ""),
            "author_username": author.get("handle"),
            "author_profile_url": f"https://bsky.app/profile/{author.get('handle')}",
            "post_url": _build_post_url(post),
            "timestamp": parse_datetime(record.get("createdAt"))
            if record.get("createdAt") else None,
            "media_url": _extract_media_url(post),
            "hashtags": _extract_hashtags(post),
        })

    return normalized


def _extract_hashtags(post: dict) -> list[str]:
    """Extract hashtag strings from a Bluesky post's rich-text facets."""
    hashtags = []
    for facet in post.get("record", {}).get("facets", []):
        for feature in facet.get("features", []):
            if feature.get("$type") == "app.bsky.richtext.facet#tag":
                hashtags.append(f"#{feature.get('tag')}")
    return hashtags


def _extract_media_url(post: dict) -> str | None:
    """Return the first image URL from a Bluesky post, if any."""
    images = post.get("embed", {}).get("images", [])
    if images:
        return images[0].get("fullsize")
    return None


def _build_post_url(post: dict) -> str:
    """Build a bsky.app permalink from a post's URI."""
    uri = post.get("uri", "")
    parts = uri.split("/")
    if len(parts) >= 5:
        did = parts[2]
        rkey = parts[-1]
        return f"https://bsky.app/profile/{did}/post/{rkey}"
    return ""
