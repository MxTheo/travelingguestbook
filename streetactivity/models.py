from mailbox import ExternalClashError
from django.db import models

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
    activity    = models.ForeignKey(StreetActivity, on_delete=models.CASCADE,
                                    related_name='experiences', verbose_name="Gerelateerde activiteit")
    report      = models.TextField(max_length=1000, verbose_name="Verslag van de ervaring")
    external_link = models.URLField(blank=True, null=True, 
                                    verbose_name="Externe link naar meer informatie, zoals een blog (optioneel)")
    fase    = models.CharField(max_length=15,
                                choices=FASE_CHOICES, default='pioneer',
                                verbose_name="Fase van de ervaring")
    fromPractitioner = models.BooleanField(default=False, 
                                           verbose_name="Is deze ervaring van een beoefenaar?")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return str(self.report[:50]) + '...'
    
class Tag(models.Model):
    """A tag is a label that can be associated with an experience of a street activity."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Naam van de tag")
    experiences = models.ManyToManyField(Experience, related_name='tags', blank=True,
                                         verbose_name="Ervaringen geassocieerd met deze tag")

    def __str__(self):
        return str(self.name)