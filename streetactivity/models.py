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
    blog        = models.URLField(blank=True,
                                verbose_name="Link naar een blogpost over de activiteit")
    literature  = models.CharField(max_length=200, blank=True, verbose_name="Relevante literatuur")
    needHelp = models.BooleanField(default=True, verbose_name="Experimenteel")

    def __str__(self):
        return str(self.name)
