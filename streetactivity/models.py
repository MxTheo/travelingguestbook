from django.db import models
from django.utils import timezone

METHOD_CHOICES = [
    ("invite", "Uitnodigen"),
    ("approach", "Aanspreken"),
    ("both", "Beide"),
]

class StreetActivity(models.Model):
    """A street activity is an activity that can be done on the street to engage with strangers."""

    name = models.CharField(max_length=100, verbose_name="Naam van het spel")
    description = models.TextField(
        max_length=3000, verbose_name="Beschrijving van het spel"
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
        max_length=300, verbose_name="Benodigdheden voor het spel"
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Order by name and set verbose names."""
        verbose_name = "straatspel"
        verbose_name_plural = "Straatspellen"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)

class Reflection(models.Model):
    """A reflection is a player's thought or feeling about doing a street activity."""

    activity = models.ForeignKey(
        "StreetActivity",
        on_delete=models.CASCADE,
        related_name="reflections",
        verbose_name="Gerelateerde activiteit",
        null=True,
        blank=True,
    )
    reflection = models.CharField(
        max_length=1000,
        verbose_name="Reflectie over het spel",
        help_text="Hoe heb je het doen van dit spel ervaren?",
    )

    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    class Meta:
        """Order reflections by date in descending order."""
        ordering = ["-date_created"]
        verbose_name = "Reflectie"
        verbose_name_plural = "Reflecties"
        indexes = [
            models.Index(fields=['activity', 'date_created']),
        ]

    def __str__(self):
        return self.reflection
