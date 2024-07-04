from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from goalmanagement.models import Goal

class Sociable(models.Model):
    '''The object that is passed from person to person'''
    slug          = models.SlugField(verbose_name='Code used to find the sociable',max_length=8,unique=True, editable=False)
    owner         = models.ForeignKey(User, verbose_name=("User of the sociable"), on_delete=models.CASCADE)
    goal          = models.ForeignKey(Goal, verbose_name=("What do you want to achieve?"), on_delete=models.CASCADE)
    description   = models.TextField(max_length=3000)
    date_modified = models.DateTimeField(auto_now=True)
    date_created  = models.DateTimeField(auto_now_add=True)

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
    name          = models.CharField(max_length=70, default='Anonymous', verbose_name='Your name')
    body          = models.TextField(max_length=30000, verbose_name='Message')
    date_created  = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_modified', '-date_created']

    def __str__(self):
        return str(self.body[0:50]+' . . .')

    def get_absolute_url(self):
        '''After entering a message,
        the visitor is redirected towards the sociable page'''
        return reverse("sociable", kwargs={"slug": self.sociable.slug})
    