"""Custom Django path converters for usermanagement URLs."""

from __future__ import annotations

from django.urls import register_converter

from usermanagement.reserved import is_reserved


class UsernameConverter:
    """Path converter for usernames in root-level profile URLs.

    Matches a URL-safe username and rejects any value that collides with
    a reserved top-level URL segment (e.g. ``admin``, ``contact``). This
    keeps the catch-all ``/<username>/`` route from shadowing real pages.
    """

    regex = r"[a-zA-Z0-9_.-]+"

    def to_python(self, value: str) -> str:
        """Convert the URL fragment to a Python value.

        Args:
            value: The raw URL fragment.

        Returns:
            The validated username.

        Raises:
            ValueError: If the username is reserved.
        """
        if is_reserved(value):
            raise ValueError(f"Username {value!r} is reserved.")
        return value

    def to_url(self, value: str) -> str:
        """Convert a Python value back into a URL fragment.

        Args:
            value: The username.

        Returns:
            The username as it should appear in a URL.
        """
        return value


register_converter(UsernameConverter, "username")
