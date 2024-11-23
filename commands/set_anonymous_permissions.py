from django.core.management.base import BaseCommand
from machina.apps.forum_permission.models import ForumPermission, Forum
from django.contrib.auth.models import Group
from machina_custom.permissions import PERMISSIONS 

class Command(BaseCommand):
    """Set forum permissions for anonymous users"""
    help = 'Set forum permissions for anonymous users'

    def handle(self, *args, **kwargs):
        anonymous_group, _ = Group.objects.get_or_create(name='Anonymous')
        forums = Forum.objects.all()

        self.assign_permissions_to_anonymous(forums, anonymous_group)

        self.stdout.write(self.style.SUCCESS(
            f"Permissions successfully set for the Anonymous group on {forums.count()} forums!"
        ))

    def assign_permissions_to_anonymous(self, forums, anonymous_group):
        """Assign permissions to the Anonymous group for each forum"""
        for forum in forums:
            for permission_type, defaults in PERMISSIONS.items():
                ForumPermission.objects.update_or_create(
                    group=anonymous_group,
                    forum=forum,
                    permission_type=permission_type,
                    defaults=defaults
                )