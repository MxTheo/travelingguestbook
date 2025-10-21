from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


METHOD_CHOICES = [
    ('invite', 'Uitnodigen'),
    ('approach', 'Aanspreken'),
    ('both', 'Beide'),
]
FASE_CHOICES = [
    ('pioneer', 'pionierservaring'),
    ('intermediate', 'overgangservaring'),
    ('climax', 'climaxervaring'),
]
NVC_CHOICES = [
    ('needs', 'behoeften'),
    ('feelings fulfilled', 'gevoelens bij vervulde behoeften'),
    ('feelings unfulfilled', 'gevoelens bij onvervulde behoeften'),
    ('other', 'anders'),
]


class StreetActivity(models.Model):
    '''A street activity is an activity that can be done on the street to engage with strangers.'''
    name        = models.CharField(max_length=100, verbose_name="Naam van de activiteit")
    description = models.TextField(max_length=500, verbose_name="Beschrijving van de activiteit")
    method      = models.CharField(max_length=10,
                              choices=METHOD_CHOICES, default='invite',
                              verbose_name="Methode van benadering")
    question    = models.CharField(max_length=200,
                                verbose_name="Kernvraag, waarmee je de ander uitnodigt of aanspreekt")
    supplies    = models.TextField(max_length=300, verbose_name="Benodigdheden voor de activiteit")

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)

class Experience(models.Model):
    '''An experience is a report of someone who has done a street activity.'''

    activity = models.ForeignKey(
        'StreetActivity',
        on_delete=models.CASCADE,
        related_name='experiences',
        verbose_name="Gerelateerde activiteit"
    )
    report = models.TextField(
        max_length=1000, 
        verbose_name="Verslag van de ervaring", 
        blank=True,
        help_text="Beschrijf de ervaring in maximaal 1000 karakters"
    )
    external_link = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Externe link naar meer informatie",
        help_text="Link naar een blog of andere informatie (optioneel)"
    )
    fase = models.CharField(
        max_length=15,
        choices=FASE_CHOICES,
        default='pioneer',
        verbose_name="Fase van de ervaring"
    )
    from_practitioner = models.BooleanField(
        default=False,
        verbose_name="Is deze ervaring van een beoefenaar?"
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='experiences',
        blank=True,
        verbose_name="Tags voor deze ervaring"
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Ervaring"
        verbose_name_plural = "Ervaringen"
        indexes = [
            models.Index(fields=['-date_created']),
            models.Index(fields=['fase']),
            models.Index(fields=['from_practitioner']),
        ]

    def __str__(self):
        if self.report:
            return f"{self.report[:50]}..."
        return f"{self.activity.name} - Ervaring {self.id}"
    
    def clean(self):
        """Validation logic"""
        if self.external_link and not self.report.strip():
            raise ValidationError({
                'report': 'Vul een verslag in wanneer een externe link wordt toegevoegd.'
            })

    @property
    def short_report(self):
        """Property for short summary of the report"""
        return self.report[:100] + '...' if len(self.report) > 100 else self.report

class Tag(models.Model):
    """A tag is a label that can be associated with an experience of a street activity."""
    
    name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Naam van de tag"
    )
    nvc_category = models.CharField(
        max_length=25,
        choices=NVC_CHOICES, 
        default='needs',
        verbose_name="Behoefte of gevoel"
    )
    main_tag = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sub_tags',
        verbose_name="Hoofdtag",
        help_text="Selecteer een hoofdtag als dit een subtag is."
    )
    description = models.TextField(
        blank=True,
        verbose_name="Beschrijving van de tag"
    )

    class Meta:
        ordering = ['nvc_category', 'name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

    def clean(self):
        """Voorkom circulaire referenties"""
        if self.main_tag and self.main_tag == self:
            raise ValidationError({
                'main_tag': 'Een tag kan niet zijn eigen hoofdtag zijn.'
            })
        if self.main_tag and self.main_tag.main_tag:
            # Voorkom diepe nesting (optioneel, afhankelijk van je behoeften)
            raise ValidationError({
                'main_tag': 'Alleen tags zonder hoofdtag kunnen als hoofdtag worden geselecteerd.'
            })

    @property
    def is_main_tag(self):
        """Check of dit een hoofdtag is"""
        return self.main_tag is None

    @property
    def has_subtags(self):
        """Check of deze tag subtags heeft"""
        return self.sub_tags.exists()

    def get_all_related_experiences(self):
        """Get all experiences related to this tag and its subtags"""
        if self.is_main_tag:
            subtags = self.sub_tags.all()
            return Experience.objects.filter(
                models.Q(tags=self) | models.Q(tags__in=subtags)
            ).distinct()
        else:
            return Experience.objects.filter(tags=self).distinct()