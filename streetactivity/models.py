from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

METHOD_CHOICES = [
    ("invite", "Uitnodigen"),
    ("approach", "Aanspreken"),
    ("both", "Beide"),
]

class StreetActivity(models.Model):
    """A street activity is an activity that can be done on the street to engage with strangers."""

    name = models.CharField(max_length=100, verbose_name="Naam van deze activiteit")
    description = models.TextField(
        max_length=3000, verbose_name="Beschrijving van de activiteit"
    )
    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default="invite",
        verbose_name="Methode van benadering",
    )
    question = models.CharField(
        max_length=200,
        verbose_name="Kernvraag, waarmee je de ander uitnodigt of aanspreekt",
    )
    supplies = models.TextField(
        max_length=300, verbose_name="Benodigdheden voor de activiteit"
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Order by name and set verbose names."""
        verbose_name = "straatactiviteit"
        verbose_name_plural = "Straatactiviteiten"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)
class Reflection(models.Model):
    """
    A reflection is a user's thought or feeling about participating in a street activity.
    Can be created locally or imported from external platforms (e.g., Mastodon, Bluesky).
    """

    activity = models.ForeignKey(
        "StreetActivity",
        on_delete=models.CASCADE,
        related_name="reflections",
        verbose_name="Related activity",
        null=True,
        blank=True,
    )
    reflection = models.TextField(
        max_length=1000,
        verbose_name="Reflection about the activity",
        help_text="Hoe heb je het doen van deze activiteit ervaren?",
    )

    # Fields for external data (e.g., from social media platforms)
    external_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,  # Voeg deze toe voor betere performance
        verbose_name="Externe ID",
        help_text="De unieke ID van de post op het externe platform (bijv. Mastodon).",
        blank=True,
        null=True,
    )
    platform = models.CharField(
        max_length=20,
        verbose_name="Platform",
        help_text="The platform where the reflection originated (e.g., Mastodon, Bluesky).",
        blank=True,
        null=True,
    )
    author_username = models.CharField(
        max_length=255,
        verbose_name="Username",
        help_text="The username of the author of the reflection.",
        blank=True,
        null=True,
    )
    author_profile_url = models.URLField(
        verbose_name="Profile URL",
        help_text="The URL of the author's profile.",
        blank=True,
        null=True,
    )
    post_url = models.URLField(
        verbose_name="Post URL",
        help_text="The URL of the original post.",
        blank=True,
        null=True,
    )
    timestamp = models.DateTimeField(
        verbose_name="Date and time of the post",
        help_text="When the reflection was shared.",
        blank=True,
        null=True,
    )
    media_url = models.URLField(
        verbose_name="Media URL",
        help_text="URL of an image or video associated with the reflection.",
        blank=True,
        null=True,
    )
    hashtags = models.JSONField(
        default=list,
        verbose_name="Hashtags",
        help_text="List of hashtags in the reflection.",
        blank=True,
    )

    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    class Meta:
        """Order reflections by date in descending order."""
        ordering = ["-date_created"]
        verbose_name = "Reflection"
        verbose_name_plural = "Reflections"
        indexes = [
            models.Index(fields=['activity', 'date_created']),
            models.Index(fields=['platform', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.reflection[:50]}... ({self.platform or 'local'})"

class StreetActivityPhoto(models.Model):
    """
    A photo uploaded for a street activity.
    Photos are directly linked to a StreetActivity and are visible immediately after upload.
    """
    activity = models.ForeignKey(
        'StreetActivity',
        on_delete=models.CASCADE,
        related_name='photos',
        help_text="The street activity this photo belongs to."
    )
    image = models.ImageField(
        upload_to='street_activity_photos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a photo of the street activity (JPG, JPEG, or PNG)."
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the photo was uploaded."
    )

    class Meta:
        verbose_name = "Street Activity Photo"
        verbose_name_plural = "Street Activity Photos"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.activity} - {self.uploaded_at}"
