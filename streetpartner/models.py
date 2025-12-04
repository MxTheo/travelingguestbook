from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class PartnershipRequest(models.Model):
    """Model voor partnerverzoeken"""
    STATUS_CHOICES = [
        ('pending', 'In afwachting'),
        ('accepted', 'Geaccepteerd'),
        ('rejected', 'Afgewezen'),
        ('cancelled', 'Geannuleerd'),
        ('expired', 'Verlopen'),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_partnership_requests',
        verbose_name="Verzonden door"
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_partnership_requests',
        verbose_name="Ontvangen door"
    )

    message = models.TextField(
        verbose_name="Persoonlijk bericht",
        max_length=500,
        blank=True,
        help_text="Optioneel bericht (max 500 tekens)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        verbose_name="Verloopt op",
        help_text="Verzoek verloopt automatisch na 14 dagen"
    )

    class Meta:
        verbose_name = "Partnerverzoek"
        verbose_name_plural = "Partnerverzoeken"
        unique_together = ['from_user', 'to_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Partnerverzoek van {self.from_user} naar {self.to_user}"

    def save(self, *args, **kwargs):
        """Set expiration date at creation"""
        if not self.pk:
            self.expires_at = timezone.now() + timezone.timedelta(days=14)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if request is expired"""
        return timezone.now() > self.expires_at

    def can_accept(self):
        """Check if request can still be accepted"""
        return (
            self.status == 'pending' and 
            not self.is_expired()
        )

    def clean(self):
        """Validation if partnership request is
        - Directed to a different user then themself
        - Not yet streetpartners
        - Directed to a user that is open to streetpartners
        - Unique, that there is no pending request between the two users present"""

        if self.from_user == self.to_user:
            raise ValidationError("Je kunt jezelf niet uitnodigen")

        existing_partnership = StreetPartnership.objects.filter(
            models.Q(user1=self.from_user, user2=self.to_user) |
            models.Q(user1=self.to_user, user2=self.from_user),
            is_active=True
        ).exists()

        if existing_partnership:
            raise ValidationError("Jullie zijn al straatpartners")

        if not self.to_user.profile.is_open_for_partnerships:
            raise ValidationError("Deze gebruiker staat niet open voor nieuwe partners")

        if self.pk is None:
            existing_request = PartnershipRequest.objects.filter(
                from_user=self.from_user,
                to_user=self.to_user,
                status__in=['pending', 'accepted']
            ).exists()

            if existing_request:
                raise ValidationError("Er bestaat al een verzoek tussen jullie")

class StreetPartnership(models.Model):
    """Model for the connection between two users"""

    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='initiated_partnerships',
        verbose_name="Gebruiker 1"
    )

    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_partnerships',
        verbose_name="Gebruiker 2"
    )

    partnership_request = models.OneToOneField(
        PartnershipRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Origineel verzoek"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(
        auto_now=True,
        verbose_name="Laatste interactie"
    )

    # Settings
    show_moments = models.BooleanField(
        default=True,
        verbose_name="Toon momenten aan elkaar"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actief partnerschap"
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Beëindigd op"
    )

    class Meta:
        verbose_name = "Straatpartnerschap"
        verbose_name_plural = "Straatpartnerschappen"
        unique_together = ['user1', 'user2']
        ordering = ['-last_interaction']

    def __str__(self):
        return f"Partnerschap tussen {self.user1} en {self.user2}"

    @property
    def partners(self):
        """Return both partners"""
        return [self.user1, self.user2]

    def get_partner(self, user):
        """Get the partner of the user"""
        if user == self.user1:
            return self.user2
        elif user == self.user2:
            return self.user1
        return None

    def clean(self):
        """Validatie: voorkom zelf-partnerschap"""
        if self.user1 == self.user2:
            raise ValidationError("Een gebruiker kan niet zijn eigen partner zijn")

    def end_partnership(self):
        """Deactivate partnership and set end date"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()

    @classmethod
    def get_partnership(cls, user1, user2):
        """Retrieve partnership between two users"""
        try:
            return cls.objects.get(
                models.Q(user1=user1, user2=user2) |
                models.Q(user1=user2, user2=user1),
                is_active=True
            )
        except cls.DoesNotExist:
            return None
