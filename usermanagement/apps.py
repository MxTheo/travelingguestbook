from django.apps import AppConfig

class UsermanagementConfig(AppConfig):
    """Configuration for the usermanagement app.

    Imports the custom path converters on startup so they are registered
    before any URLconf is resolved.
    Also imports the signals module to ensure that signal handlers are connected.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usermanagement'

    def ready(self):
        """Signals are imported once the app is ready"""
        from usermanagement import (
            converters,  # noqa: F401
            signals,
        )
