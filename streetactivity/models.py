from django.db import models
from django.core.exceptions import ValidationError


METHOD_CHOICES = [
    ("invite", "Uitnodigen"),
    ("approach", "Aanspreken"),
    ("both", "Beide"),
]
FASE_CHOICES = [
    ("pioneer", "onzeker"),
    ("intermediate", "tussenin"),
    ("climax", "zelfverzekerd"),
]
NVC_CHOICES = [
    ("needs", "Behoeften"),
    ("feelings_fulfilled", "Gevoelens bij vervulde behoeften"),
    ("feelings_unfulfilled", "Gevoelens bij onvervulde behoeften"),
    ("other", "Anders"),
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
    """An experience is a report of someone who has done a street activity."""

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
    external_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Externe link naar meer informatie",
        help_text="Link naar een blog of andere informatie (optioneel)",
    )
    fase = models.CharField(
        max_length=15,
        choices=FASE_CHOICES,
        default="pioneer",
        verbose_name="Zelfverzekerdheid",
    )
    from_practitioner = models.BooleanField(
        default=True, verbose_name="Is deze ervaring van een beoefenaar?"
    )
    tags = models.ManyToManyField(
        "Tag",
        related_name="experiences",
        blank=True,
        verbose_name="Tags voor deze ervaring",
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Ervaring"
        verbose_name_plural = "Ervaringen"
        indexes = [
            models.Index(fields=["-date_created"]),
            models.Index(fields=["fase"]),
            models.Index(fields=["from_practitioner"]),
        ]

    def __str__(self):
        if self.report:
            return f"{self.report[:50]}..."
        return f"{self.activity.name} - Ervaring {self.id}"

    def clean(self):
        """Validation logic"""
        if self.external_link and not self.report.strip():
            raise ValidationError(
                {
                    "report": "Vul een verslag in wanneer een externe link wordt toegevoegd."
                }
            )

class Tag(models.Model):
    """A tag is a label that can be associated with an experience of a street activity."""

    name = models.CharField(max_length=50, unique=True, verbose_name="Naam van de tag")
    nvc_category = models.CharField(
        max_length=25,
        choices=NVC_CHOICES,
        default="needs",
        verbose_name="Behoefte of gevoel",
    )
    maintag = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subtags",
        verbose_name="Hoofdtag",
        help_text="Selecteer een hoofdtag als dit een subtag is.",
    )

    class Meta:
        ordering = ["nvc_category", "name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        """Return the name of the tag"""
        return str(self.name)

    def clean(self):
        """Prohibit circular references and deep nesting of tags."""
        if self.maintag and self.maintag == self:
            raise ValidationError(
                {"maintag": "Een tag kan niet zijn eigen hoofdtag zijn."}
            )
        if self.maintag and self.maintag.maintag:
            raise ValidationError(
                {
                    "maintag": "Alleen tags zonder hoofdtag kunnen als hoofdtag worden geselecteerd"
                }
            )

    @property
    def is_maintag(self):
        """Check if this tag is a main tag"""
        return self.maintag is None

    @property
    def has_subtags(self):
        """Check if this tag has subtags"""
        return self.subtags.exists()

    def get_all_related_experiences(self):
        """Get all experiences related to this tag and its subtags"""
        if self.is_maintag:
            subtags = self.subtags.all()
            return Experience.objects.filter(
                models.Q(tags=self) | models.Q(tags__in=subtags)
            ).distinct()
        else:
            return Experience.objects.filter(tags=self).distinct()
