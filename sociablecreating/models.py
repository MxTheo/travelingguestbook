from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from goalmanagement.models import Goal

class Sociable(models.Model):
    slug          = models.SlugField(verbose_name='Code used to find the sociable',max_length=8,unique=True, editable=False)
    owner         = models.ForeignKey(User, verbose_name=("User of the sociable"), on_delete=models.CASCADE)
    goal          = models.ForeignKey(Goal, verbose_name=("What do you want to achieve?"), on_delete=models.CASCADE)
    description   = models.TextField(max_length=3000)
    date_modified = models.DateTimeField(auto_now=True)
    date_created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def get_absolute_url(self):
        return reverse("sociable", kwargs={"slug": self.slug})

    def __str__(self):
        return self.slug
    
class LogMessage(models.Model):
    sociable      = models.ForeignKey(Sociable, on_delete=models.CASCADE)
    name          = models.CharField(max_length=70, default='Philosopher', verbose_name='Your name')
    body          = models.TextField(max_length=300, verbose_name='Message')
    date_created  = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_modified', '-date_created']

    def __str__(self):
        return self.body[0:50]+' . . .'
    
    def get_absolute_url(self):
        return reverse("sociable", kwargs={"slug": self.sociable.slug})
    