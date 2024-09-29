from django.db import models
from django.contrib.auth.models import User

 # Create your models here.
# class Level(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     lvl = models.IntegerField(verbose_name='level van de gebruiker', default=0)
#     xp_next_lvl = models.IntegerField(verbose_name='De benodigde xp voor het volgende level', default=1)
#     xp = models.IntegerField(verbose_name='Het totaal xp van de gebruiker', default=0)