from django.contrib.auth import get_user_model
from django.db import models


class CookieConsentLog(models.Model):
    """A log of a user's cookie consent decision."""
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    consent = models.JSONField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
