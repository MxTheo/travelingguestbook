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
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)
