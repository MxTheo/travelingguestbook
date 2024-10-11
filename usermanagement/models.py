from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    '''Extending the user model by a profile, used the tutorials:

    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

    https://dev.to/earthcomfy/django-user-profile-3hik
    '''
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, blank=True)

    lvl         = models.IntegerField(verbose_name='level van de gebruiker', default=0)
    xp_next_lvl = models.IntegerField(verbose_name='De benodigde xp voor het volgende level', default=1)
    xp   = models.IntegerField(verbose_name='De behaalde xp', default=0)
    xp_start_lvl = models.IntegerField(verbose_name='De start xp van het level', default=0)

    def __str__(self):
        return self.user.username
