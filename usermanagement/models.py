from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    """Profile to extend the user and store more information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    lvl = models.IntegerField(default=0)

    def __str__(self):
        return f"Profile of '{self.user.username}'"