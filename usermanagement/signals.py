from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from usermanagement.models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    '''Every time a user is created, a new profile is create.
    Thus, a new profile is only created when a user is created.'''
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    '''Every time a user is saved, the profile is saved as well
    Thus, a profile is also saved, when a user is updated, withouth being a newly created user'''
    instance.profile.save()
