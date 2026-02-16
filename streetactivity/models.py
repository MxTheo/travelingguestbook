import uuid
from django.db import models

METHOD_CHOICES = [
    ("invite", "Uitnodigen"),
    ("approach", "Aanspreken"),
    ("both", "Beide"),
]

class StreetActivity(models.Model):
    """A street activity is an activity that can be done on the street to engage with strangers."""

    name = models.CharField(max_length=100, verbose_name="Naam van de activiteit")
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
        verbose_name = "Straatactiviteit"
        verbose_name_plural = "Straatactiviteiten"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)

class ConfidenceLevel(models.IntegerChoices):
    """Choices for confidence level."""
    ONZEKER       = 0, "onzeker"
    TUSSENIN      = 1, "tussenin"
    ZELFVERZEKERD = 2, "zelverzekerd"

class Moment(models.Model):
    """An moment is a report of a moment of someone who has done a street activity."""

    experience = models.ForeignKey(
        "Experience",
        on_delete=models.CASCADE,
        related_name="moments",
        verbose_name="Gerelateerde ervaring",
        null=True,
        blank=True,
    )
    activity = models.ForeignKey(
        "StreetActivity",
        on_delete=models.CASCADE,
        related_name="moments",
        verbose_name="Gerelateerde activiteit",
        null=True,
        blank=True,
    )
    report = models.TextField(
        max_length=367,
        verbose_name="Wat voelde je? Wat ging er in je om?",
        blank=True,
        help_text="Beschrijf wat zich aandiende in maximaal 367 karakters",
    )
    confidence_level = models.IntegerField(
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.ONZEKER,
        verbose_name="Zelfverzekerdheid",
    )
    from_practitioner = models.BooleanField(
        default=True, verbose_name="Is deze ervaring van een beoefenaar?"
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Order moments by date in descending order."""
        ordering = ["-date_created"]
        verbose_name = "Moment"
        verbose_name_plural = "Momenten"
        indexes = [
            models.Index(fields=["-date_created"]),
            models.Index(fields=["confidence_level"]),
            models.Index(fields=["from_practitioner"]),
        ]

    def __str__(self):
        if self.report:
            return f"{self.report[:50]}..."
        return f"{self.activity.name} - Moment {self.id}"

class Experience(models.Model):
    """An experience is a collection of moments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="experiences",
        verbose_name="Speler",
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Ervaring"
        verbose_name_plural = "Ervaringen"

    def __str__(self):
        return f"Ervaring {self.date_created.strftime('%d-%m-%Y %H:%M')}"
