from django.db import models

METHOD_CHOICES = [
    ('invite', 'Uitnodigen'),
    ('approach', 'Aanspreken'),
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
    difficulty = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3, 
                                     verbose_name="Moeilijkheidsgraad (1-5)")
    chance      = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3, 
                                 verbose_name="Kans op contact (1-5)")
    extension   = models.TextField(max_length=300, blank=True,
                                 verbose_name="Uitbreiding of variatie op de activiteit")
    needHelp    = models.BooleanField(default=True, verbose_name="Experimenteel")

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)

# models.py
class ExternalReference(models.Model):
    """
    Decentralized references to anything relevant to a street activity:
    experiences, sources of inspiration, research, theory, etc.
    """
    activity = models.ForeignKey(
        StreetActivity,
        on_delete=models.CASCADE,
        related_name='external_references'
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Titel van de referentie"
    )
    description = models.TextField(
        max_length=500,
        verbose_name="Beschrijving of samenvatting",
        help_text="Wat is de relatie met deze straatactiviteit?"
    )
    url = models.URLField(
        blank=True,
        verbose_name="Link (optioneel)",
        help_text="URL naar blog, video, artikel, etc. Niet verplicht voor boeken/theorie."
    )
    reference_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Soort referentie (optioneel)",
        help_text="Bijv: persoonlijke ervaring, boek, onderzoek, theorie, inspiratie..."
    )
    submitted_by = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Ingediend door (optioneel)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Externe Referentie"
        verbose_name_plural = "Externe Referenties"

    def __str__(self):
        return f"{self.title} - {self.activity.name}"
