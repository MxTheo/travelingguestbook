from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Sociable(models.Model):
    '''The object that is passed from person to person'''
    slug          = models.SlugField(verbose_name='Code om de sociable te kunnen vinden', max_length=8, unique=True, editable=False)
    owner         = models.ForeignKey(User, on_delete=models.CASCADE)
    description   = models.TextField(max_length=3000, blank=True, help_text='Vrije ruimte en optioneel: Misschien heb je wel iets wat je wilt weten van anderen. Hier is de ruimte om verzoeken te doen aan degene die hier een berichtje achter laten', verbose_name='Omschrijving', default='Ik heb een bericht voor je achter gelaten. Leuk als je reageert, hoeft niet. Vertel iets over jouw ervaringen van ons gesprek. Nu is het aan jou om deze gespreksketen voor te zetten.')
    date_created  = models.DateTimeField(auto_now_add=True, verbose_name='Datum aangemaakt')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='Datum aangepast')

    class Meta:
        ordering = ['-date_created']

    def get_absolute_url(self):
        '''Given the code of the sociable (slug),
        returns the url with the code appended after,
        so that sociablepage is findable by the reciever of the sociable'''
        return reverse("sociable", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.slug)


class LogMessage(models.Model):
    '''The message the receiver of the sociable leaves on the sociable page'''
    sociable      = models.ForeignKey(Sociable, on_delete=models.CASCADE)
    author        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name          = models.CharField(max_length=70, default='Anoniem', verbose_name='Je naam', help_text='Een naam geeft al context aan een bericht. Voel je ook vrij om je naam op anoniem te houden')
    body          = models.TextField(max_length=30000, verbose_name='Bericht', help_text='Vertel iets over je ervaringen van het gesprek. Voel je vrij te delen wat je wilt delen en niet te delen wat je niet wilt delen.')
    date_created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        '''Put the messages that are most recently modified, then put the messages that are most recently created'''
        ordering = ['-date_created']

    def __str__(self):
        return str(self.body[0:50]+' . . .')

    def get_absolute_url(self):
        '''After entering a message,
        the visitor is redirected towards the sociable page'''
        return reverse("sociable", kwargs={"slug": self.sociable.slug})
