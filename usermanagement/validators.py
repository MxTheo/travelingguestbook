"""Validators for usermanagement models and forms."""

from __future__ import annotations

from django.core.exceptions import ValidationError

from usermanagement.reserved import is_reserved


def validate_username_not_reserved(username) -> None:
    """Reject usernames that collide with a reserved URL segment.

    Args:
        value: The username to validate.

    Raises:
        ValidationError: If the username is reserved.
    """
    if is_reserved(username):
        raise ValidationError(
            "%(value)s is gereserveerd en kan niet als gebruikersnaam "
            "worden gebruikt.",
            params={"value": username},
        )
