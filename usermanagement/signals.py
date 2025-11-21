# myproject/userprofile/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from usermanagement.models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, *args, **kwargs):
    """When a user is created, create a profile, else save the current profile"""
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()