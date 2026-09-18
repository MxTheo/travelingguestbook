"""Utilities for discovering reserved URL segments.

The username profile URL is a catch-all at the root of the site
(``/<username>/``). Any top-level URL pattern that is registered *before*
this catch-all effectively reserves its first path segment, because it
will always be matched first. If a user were allowed to register such a
name, their profile would be unreachable.

This module introspects the project's root URLconf and collects those
reserved segments automatically, so the list does not need to be kept in
sync by hand.
"""

from __future__ import annotations

from functools import lru_cache

from django.urls import URLPattern, URLResolver, get_resolver

#: Segments that are always reserved regardless of the URLconf, because
#: they are needed by Django itself or by static/media serving.
STATIC_RESERVED: frozenset[str] = frozenset(
    {
        "admin",
        "static",
        "media",
    }
)


def _first_segment(pattern: str) -> str | None:
    """Return the first non-empty path segment of a URL pattern.

    Args:
        pattern: A URL pattern string such as ``"accounts/"`` or
            ``"<username:username>/"``.

    Returns:
        The first literal segment without slashes, or ``None`` if the
        pattern has no literal first segment (e.g. it starts with a
        converter or is empty).
    """
    segment = pattern.strip("/").split("/", 1)[0]
    if not segment or segment.startswith("<"):
        return None
    return segment


def collect_reserved_segments() -> set[str]:
    """Collect all reserved first-segment URL names from the root URLconf.

    Walks the project's root URLResolver and gathers the first path
    segment of every top-level pattern that is not itself a catch-all
    (i.e. does not start with a converter). The result includes both the
    literal segments found in the URLconf and the always-reserved names
    in :data:`STATIC_RESERVED`.

    Returns:
        A set of lowercase reserved segment names.
    """
    reserved: set[str] = set(STATIC_RESERVED)
    resolver = get_resolver()

    for pattern in resolver.url_patterns:
        if isinstance(pattern, URLResolver):
            segment = _first_segment(str(pattern.pattern))
        elif isinstance(pattern, URLPattern):
            segment = _first_segment(str(pattern.pattern))
        else:  # pragma: no cover - defensive
            continue

        if segment:
            reserved.add(segment.lower())

    return reserved


@lru_cache(maxsize=1)
def reserved_segments() -> frozenset[str]:
    """Return the cached set of reserved URL segments.

    The result is cached because the URLconf is effectively immutable at
    runtime. Tests that modify ``ROOT_URLCONF`` should call
    :func:`reserved_segments.cache_clear` to invalidate the cache.

    Returns:
        A frozen set of lowercase reserved segment names.
    """
    return frozenset(collect_reserved_segments())


def is_reserved(value: str) -> bool:
    """Check whether a given username collides with a reserved segment.

    Args:
        value: The username to check.

    Returns:
        ``True`` if the username (case-insensitively) matches a reserved
        segment, ``False`` otherwise.
    """
    return value.lower() in reserved_segments()