from weaktie.forms import ContactChannelForm
from weaktie.models import ContactChannel


class TestContactChannelFormValid:
    """Tests for valid input to ContactChannelForm."""

    def test_valid_with_known_app(self):
        """A known app without app_other should be valid and clear app_other."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.SIGNAL,
                "url": "https://signal.me/#eu/abc123",
            }
        )

        assert form.is_valid(), form.errors
        assert form.cleaned_data["app"] == ContactChannel.App.SIGNAL
        assert form.cleaned_data["app_other"] == ""

    def test_valid_with_other_app_and_name(self):
        """Selecting 'Other' with a name should be valid and keep the name."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.OTHER,
                "app_other": "Telegram",
                "url": "https://t.me/someuser",
            }
        )

        assert form.is_valid(), form.errors
        assert form.cleaned_data["app"] == ContactChannel.App.OTHER
        assert form.cleaned_data["app_other"] == "Telegram"

    def test_app_other_is_stripped(self):
        """Whitespace around app_other should be removed."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.OTHER,
                "app_other": "  Telegram  ",
                "url": "https://t.me/someuser",
            }
        )

        assert form.is_valid(), form.errors
        assert form.cleaned_data["app_other"] == "Telegram"


class TestContactChannelFormInvalid:
    """Tests for invalid input to ContactChannelForm."""

    def test_other_app_without_name_is_invalid(self):
        """Selecting 'Other' without a name should raise an error on app_other."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.OTHER,
                "app_other": "",
                "url": "https://t.me/someuser",
            }
        )

        assert not form.is_valid()
        assert "app_other" in form.errors

    def test_other_app_with_only_whitespace_is_invalid(self):
        """A whitespace-only app_other should be treated as empty."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.OTHER,
                "app_other": "   ",
                "url": "https://t.me/someuser",
            }
        )

        assert not form.is_valid()
        assert "app_other" in form.errors

    def test_known_app_with_leftover_app_other_is_cleared(self):
        """A leftover app_other for a known app should be ignored, not rejected."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.SIGNAL,
                "app_other": "Telegram",
                "url": "https://signal.me/#eu/abc123",
            }
        )

        assert form.is_valid(), form.errors
        assert form.cleaned_data["app_other"] == ""

    def test_invalid_url_is_rejected(self):
        """A malformed URL should be rejected by the URL field."""
        form = ContactChannelForm(
            data={
                "app": ContactChannel.App.SIGNAL,
                "url": "not-a-url",
            }
        )

        assert not form.is_valid()
        assert "url" in form.errors

    def test_missing_url_is_rejected(self):
        """The URL field is required."""
        form = ContactChannelForm(data={"app": ContactChannel.App.SIGNAL})

        assert not form.is_valid()
        assert "url" in form.errors

class TestContactChannelFormDisplayApp:
    """Tests for the display_app property as used by the form."""

    def test_display_app_returns_known_app(self):
        """display_app should return the app name for a known app."""
        channel = ContactChannel(app=ContactChannel.App.SIGNAL, app_other="")
        assert channel.display_app == "Signal"

    def test_display_app_returns_app_other(self):
        """display_app should return app_other when the app is Other."""
        channel = ContactChannel(
            app=ContactChannel.App.OTHER, app_other="Telegram"
        )
        assert channel.display_app == "Telegram"