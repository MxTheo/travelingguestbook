from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from streetpartner.models import StreetPartnership

METHOD_CHOICES = [
    ("invite", "Uitnodigen"),
    ("approach", "Aanspreken"),
    ("both", "Beide"),
]
CONFIDENCE_LEVEL_CHOICES = [
    ("pioneer", "onzeker"),
    ("intermediate", "tussenin"),
    ("climax", "zelfverzekerd"),
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
        verbose_name = "Straatactiviteit"
        verbose_name_plural = "Straatactiviteiten"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)


class Experience(models.Model):
    """An experience is a report of a moment of someone who has done a street activity."""

    activity = models.ForeignKey(
        "StreetActivity",
        on_delete=models.CASCADE,
        related_name="experiences",
        verbose_name="Gerelateerde activiteit",
    )
    report = models.TextField(
        max_length=3500,
        verbose_name="Wat voelde je? Wat ging er in je om?",
        blank=True,
        help_text="Beschrijf wat zich aandiende in maximaal 3500 karakters",
    )
    confidence_level = models.CharField(
        max_length=15,
        choices=CONFIDENCE_LEVEL_CHOICES,
        default="pioneer",
        verbose_name="Zelfverzekerdheid",
    )
    from_practitioner = models.BooleanField(
        default=True, verbose_name="Is deze ervaring van een beoefenaar?"
    )

    keywords = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="Kernwoorden",
        help_text="3 woorden die je moment samenvatten, gescheiden door komma's")

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Ervaring"
        verbose_name_plural = "Ervaringen"
        indexes = [
            models.Index(fields=["-date_created"]),
            models.Index(fields=["confidence_level"]),
            models.Index(fields=["from_practitioner"]),
        ]

    def __str__(self):
        if self.report:
            return f"{self.report[:50]}..."
        return f"{self.activity.name} - Ervaring {self.id}"
