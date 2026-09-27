from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Whereabout(models.Model):
    """Model representing an occassion where the user is already going to.
    Here a visitor has the opportunity to meet the user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="whereabouts")
    location = models.CharField(max_length=255)
    when = models.DateTimeField(default=timezone.now)

    class Meta:
        """Set verbose names and ordering for the Whereabout model."""
        verbose_name = "gelegenheid"
        verbose_name_plural = "gelegenheden"
        ordering = ["-when"]

    def __str__(self):
        return f"{self.user.username} is at {self.location} on {self.when}"

class Link(models.Model):
    """Model representing a link to a social media profile or website. Relevant for asynchronous contact."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links")
    url = models.URLField(max_length=500)

    class Meta:
        """Set verbose names and ordering for the Link model."""
        verbose_name = "link"
        verbose_name_plural = "links"
        ordering = ["-id"]

    @property
    def domain(self):
        """Return the domain without www."""
        return urlparse(self.url).netloc.removeprefix("www.")

    @property
    def path(self):
        """Return the path without trailing slash."""
        return urlparse(self.url).path.rstrip("/")

    def __str__(self):
        return f"{self.user.username} link: {self.url}"