import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from streetpartner.models import StreetPartnership

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
    xp_percentage_of_progress = models.IntegerField(
        verbose_name="Percentage van de xp voortgang tijdens dit lvl", default=0)

    # Partner settings - all opt-in
    is_open_for_partnerships = models.BooleanField(
        verbose_name="Sta open voor nieuwe partnerschappen",
        default=False,
        help_text="Andere gebruikers kunnen je uitnodigen als straatpartner"
    )

    # Privacy settings
    show_online_status = models.BooleanField(
        verbose_name="Toon online status",
        default=False
    )

    show_moments_to_partners = models.BooleanField(
        verbose_name="Toon mijn momenten aan mijn straatpartners",
        default=True
    )

    class Meta:
        verbose_name = "Profiel"
        verbose_name_plural = "Profielen"

    @property
    def profile_image_url(self):
        """Returns the URL of the profile image or a default image if none is set."""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/persona/images/empty_portrait.jpg'

    @property
    def current_partners_count(self):
        """Number of active streetpartnerships"""
        return StreetPartnership.objects.filter(
            models.Q(user1=self.user) | models.Q(user2=self.user),
            is_active=True
        ).count()

    @property
    def has_active_partnerships(self):
        """Check if user has active partnerships"""
        return self.current_partners_count > 0

    def __str__(self):
        return f"Profile of '{self.user.username}'"
