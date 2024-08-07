from django.apps import AppConfig


class UsermanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usermanagement'

    def ready(self):
        import usermanagement.signals
