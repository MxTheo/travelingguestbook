"""Tests for the UsernameConverter path converter."""

from __future__ import annotations

import re

import pytest

from usermanagement.converters import UsernameConverter


class TestUsernameConverter:
    """Tests for :class:`UsernameConverter`."""

    def test_to_python_accepts_free_name(self, temp_urlconf):
        """A free username is returned unchanged."""
        converter = UsernameConverter()
        assert converter.to_python("johndoe") == "johndoe"

    def test_to_python_rejects_reserved_name(self, temp_urlconf):
        """A reserved username raises ValueError."""
        converter = UsernameConverter()
        with pytest.raises(ValueError):
            converter.to_python("contact")

    def test_to_python_rejects_reserved_case_insensitive(self, temp_urlconf):
        """Reserved check is case-insensitive."""
        converter = UsernameConverter()
        with pytest.raises(ValueError):
            converter.to_python("Contact")

    def test_to_python_accepts_converter_name(self, temp_urlconf):
        """A name matching the converter is allowed if not reserved."""
        converter = UsernameConverter()
        assert converter.to_python("username") == "username"

    def test_to_url_returns_value(self):
        """to_url is the identity function."""
        converter = UsernameConverter()
        assert converter.to_url("johndoe") == "johndoe"

    def test_regex_matches_url_safe_chars(self):
        """The converter regex matches typical usernames."""
        pattern = re.compile(UsernameConverter.regex)
        assert pattern.fullmatch("john.doe-01_x")