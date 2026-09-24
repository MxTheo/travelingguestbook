from django.contrib.auth.models import User
from django.db import models


class Whereabout(models.Model):
    """Model representing an event that the user can invite their spontaneous contact for"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="whereabouts")
    location = models.CharField(max_length=255)
    date = models.DateTimeField()

    def __str__(self):
        return f"Whereabout at {self.location} on {self.date} by {self.user.username}"
