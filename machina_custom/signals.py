from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from machina.apps.forum.models import Forum
from machina.apps.forum_permission.models import ForumPermission
from machina_custom.permissions import PERMISSIONS

@receiver(post_save, sender=Forum)
def set_anonymous_permissions(sender, instance, created, **kwargs):
    """Assign permissions for the Anonymous group for newly created forums"""
    if created:
        anonymous_group, _ = Group.objects.get_or_create(name='Anonymous')

        assign_permissions_for_forum(anonymous_group, instance)

def assign_permissions_for_forum(anonymous_group, new_forum):
    """Assign permissions to the Anonymous group for the new forum"""
    for permission_type, defaults in PERMISSIONS.items():
        ForumPermission.objects.update_or_create(
            group=anonymous_group,
            forum=new_forum,
            permission_type=permission_type,
            defaults=defaults
        )