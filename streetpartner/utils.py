# partnerships/utils.py
from django.db import models
from streetactivity.models import Experience
from .models import StreetPartnership

def get_user_partners(user):
    """Haal alle actieve partners op voor een gebruiker"""
    partnerships = StreetPartnership.objects.filter(
        (models.Q(user1=user) | models.Q(user2=user)) &
        models.Q(is_active=True)
    )

    partners = []
    for partnership in partnerships:
        partner = partnership.get_partner(user)
        if partner:
            partners.append(partner)

    return partners

def are_partners(user1, user2):
    """Controleer of twee gebruikers partners zijn"""
    return StreetPartnership.objects.filter(
        (models.Q(user1=user1, user2=user2) |
         models.Q(user1=user2, user2=user1)) &
        models.Q(is_active=True) &
        models.Q(show_moments=True)
    ).exists()

def get_shared_moments(user1, user2):
    """Retrieve experiences that are shared between partners"""

    if not are_partners(user1, user2):
        return Experience.objects.none()

    return Experience.objects.filter(
        user=user2,
        user__profile__show_moments_to_partners=True
    ).order_by('-created_at')