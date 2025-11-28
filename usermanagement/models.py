import uuid
import os
from django.contrib.auth.models import User
from django.db import models

def profile_image_path(instance, filename):
    """Upload path voor persona portretten"""
    ext = filename.split('.')[-1]
    filename = f"profileimage_{uuid.uuid4().hex}.{ext}"
    return os.path.join('profile_images/', filename)

class Profile(models.Model):
    """Profile to extend the user and store more information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    date_created = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(
        upload_to=profile_image_path,
        blank=True,
        null=True,
        verbose_name="Profiel foto"
    )

    # lvl and experiences
    lvl = models.IntegerField(default=1)
    xp_next_lvl = models.IntegerField(
        verbose_name="De benodigde xp voor het volgende level", default=75)
    xp = models.IntegerField(
        verbose_name="De behaalde xp", default=0)
    xp_start = models.IntegerField(
        verbose_name="De xp waarmee is gestart in dit level", default=0)


    @property
    def profile_image_url(self):
        """Returns the URL of the profile image or a default image if none is set."""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/persona/images/empty_portrait.jpg'

    def __str__(self):
        return f"Profile of '{self.user.username}'"
