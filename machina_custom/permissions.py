"""Permissions for the anonymous users"""

PERMISSIONS = {
    'can_read_forum': {'is_active': True},
    'can_start_new_topics': {'is_active': False},
    'can_reply_to_topics': {'is_active': False},
}