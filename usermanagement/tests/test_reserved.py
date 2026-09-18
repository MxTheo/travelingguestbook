"""Tests for the dynamic reserved-segment discovery."""

from __future__ import annotations

import pytest

from usermanagement import reserved as reserved_module


class TestFirstSegment:
    """Tests for :func:`_first_segment`."""

    def test_returns_literal_segment(self):
        """A plain literal pattern yields its segment."""
        assert reserved_module._first_segment("contact/") == "contact"

    def test_strips_leading_and_trailing_slashes(self):
        """Slashes around the segment are stripped."""
        assert reserved_module._first_segment("/contact/") == "contact"

    def test_returns_none_for_empty_pattern(self):
        """An empty pattern has no segment."""
        assert reserved_module._first_segment("") is None

    def test_returns_none_for_converter_pattern(self):
        """A pattern starting with a converter has no literal segment."""
        assert reserved_module._first_segment("<username:username>/") is None

    def test_returns_first_of_multiple_segments(self):
        """Only the first segment is returned."""
        assert reserved_module._first_segment("a/b/c/") == "a"


class TestCollectReservedSegments:
    """Tests for :func:`collect_reserved_segments`."""

    def test_includes_static_reserved(self, temp_urlconf):
        """Static reserved names are always present."""
        result = reserved_module.collect_reserved_segments()
        assert reserved_module.STATIC_RESERVED <= result

    def test_includes_literal_segments(self, temp_urlconf):
        """Literal top-level segments are picked up."""
        expected = {"admin", "contact", "overons", "accounts"}
        result = reserved_module.collect_reserved_segments()
        assert expected <= result

    def test_includes_segments_from_urlresolver(self, temp_urlconf):
        """Segments from included URLconfs (URLResolver) are picked up.

        The temporary URLconf includes ``usermanagement.profile_urls``
        under ``accounts/``. That produces a ``URLResolver`` instance in
        ``resolver.url_patterns`` rather than a ``URLPattern``, so this
        exercises the ``isinstance(pattern, URLResolver)`` branch of
        :func:`collect_reserved_segments`.
        """
        result = reserved_module.collect_reserved_segments()
        assert "accounts" in result

    def test_ignores_converter_segments(self, temp_urlconf):
        """Converter patterns do not contribute a reserved segment."""
        result = reserved_module.collect_reserved_segments()
        assert "username" not in result

    def test_result_is_lowercase(self, temp_urlconf):
        """All returned segments are lowercase."""
        result = reserved_module.collect_reserved_segments()
        assert all(seg == seg.lower() for seg in result)


class TestReservedSegmentsCache:
    """Tests for the cached :func:`reserved_segments` wrapper."""

    def test_returns_frozenset(self, temp_urlconf):
        """The cached result is a frozenset."""
        assert isinstance(reserved_module.reserved_segments(), frozenset)

    def test_cache_clear_recomputes(self, temp_urlconf):
        """Clearing the cache causes recomputation."""
        first = reserved_module.reserved_segments()
        reserved_module.reserved_segments.cache_clear()
        second = reserved_module.reserved_segments()
        assert first == second


class TestIsReserved:
    """Tests for :func:`is_reserved`."""

    @pytest.mark.parametrize("name", ["admin", "ADMIN", "Contact", "contact"])
    def test_reserved_names(self, temp_urlconf, name):
        """Reserved names are detected case-insensitively."""
        assert reserved_module.is_reserved(name) is True

    def test_free_name(self, temp_urlconf):
        """A free name is not reserved."""
        assert reserved_module.is_reserved("johndoe") is False

    def test_converter_name_is_free(self, temp_urlconf):
        """A name matching a converter is not reserved."""
        assert reserved_module.is_reserved("username") is False