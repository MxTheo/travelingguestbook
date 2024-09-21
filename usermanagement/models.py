from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    '''Extending the user model by a profile, used the tutorials:

    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

    https://dev.to/earthcomfy/django-user-profile-3hik
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, blank=True)
    custom_description_for_code = models.TextField(max_length=3000, blank=True, help_text='Vul deze in als je je eigen standaard omschrijving wilt gebruiken voor codes', verbose_name='Omschrijving voor codes')

    def __str__(self):
        return self.user.username
