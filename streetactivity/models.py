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

class Moment(models.Model):
    """An moment is a report of a moment of someone who has done a street activity."""
    
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

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Order moments by date in descending order."""
        ordering = ["-date_created"]
        verbose_name = "Moment"
        verbose_name_plural = "Momenten"
        indexes = [
            models.Index(fields=["-date_created"]),
        ]

    def __str__(self):
        if self.report:
            return f"{self.report[:50]}..."
        return f"{self.activity.name} - Moment {self.id}"
