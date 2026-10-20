from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Whereabout(models.Model):
    """Model representing an occassion where the user is already going to.
    Here a visitor has the opportunity to meet the user."""
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="whereabouts")
    location = models.CharField(max_length=255)
    when     = models.DateTimeField(default=timezone.now)
    source   = models.URLField(max_length=500, blank=True, null=True, verbose_name="Bron (URL)")

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
    def handle(self):
        """Return the last segment of the URL path, or the domain if no path."""
        parsed = urlparse(self.url)
        path = parsed.path.rstrip("/")
        if path:
            return path.split("/")[-1]
        return parsed.netloc.removeprefix("www.")

    def __str__(self):
        return f"{self.user.username} link: {self.url}"

class ContactChannel(models.Model):
    """Model representing a way to reach a user via a chat application."""

    class App(models.TextChoices):
        """Supported chat applications."""
        SIGNAL = "Signal", "Signal"
        SIMPLEX = "Simplex", "Simplex"
        TELEGRAM = "Telegram", "Telegram"
        WHATSAPP = "WhatsApp", "WhatsApp"
        SLACK = "Slack", "Slack"
        SNAPCHAT = "Snapchat", "Snapchat"
        WECHAT = "WeChat", "WeChat"
        MESSENGER = "Messenger", "Messenger"
        OTHER = "Other", "Other"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contactchannels"
    )
    app = models.CharField(max_length=255, choices=App.choices)
    app_other = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=500)

    class Meta:
        """Set verbose names and ordering for the ContactChannel model."""
        verbose_name = "contactkanaal"
        verbose_name_plural = "contactkanalen"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.display_app}: {self.url[:30]}…"

    @property
    def display_app(self):
        """Return the app name to show to the receiver."""
        return self.app_other if self.app == self.App.OTHER else self.app
