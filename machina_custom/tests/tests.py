from machina.apps.forum.models import Forum
from machina.apps.forum_permission.models import ForumPermission
from django.contrib.auth.models import Group
from machina_custom.permissions import PERMISSIONS

def test_set_anonymous_permissions_signal():
    """Test if permissions to anonymous have been set when creating a new forum"""
    # Ensure the Anonymous group exists
    anonymous_group, _ = Group.objects.get_or_create(name="Anonymous")

    # Create a new forum (triggers the signal)
    forum = Forum.objects.create(name="Test Forum", slug="test-forum",type=Forum.FORUM_POST)

    # Assert that permissions have been created for the new forum
    for permission_type, defaults in PERMISSIONS.items():
        permission_exists = ForumPermission.objects.filter(
            group=anonymous_group,
            forum=forum,
            permission_type=permission_type,
            **defaults,
        ).exists()
        assert permission_exists, f"Permission {permission_type} was not created for the forum"

def test_no_duplicate_permissions_signal():
    """Test that re-saving a forum doesn't create duplicate permissions"""
    anonymous_group, _ = Group.objects.get_or_create(name="Anonymous")
    forum = Forum.objects.create(name="Test Forum", slug="test-forum",type=Forum.FORUM_POST)

    # Trigger the signal by saving the forum again
    forum.save()

    # Assert no duplicate permissions exist
    for permission_type in PERMISSIONS:
        assert ForumPermission.objects.filter(
            group=anonymous_group,
            forum=forum,
            permission_type=permission_type,
        ).count() == 1