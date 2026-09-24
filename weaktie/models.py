from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Whereabout(models.Model):
    """Model representing an occassion where the user is already going to.
    Here a visitor has the opportunity to meet the user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="whereabouts")
    location = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        """Set verbose names and ordering for the Whereabout model."""
        verbose_name = "gelegenheid"
        verbose_name_plural = "gelegenheden"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} is at {self.location} on {self.date}"
