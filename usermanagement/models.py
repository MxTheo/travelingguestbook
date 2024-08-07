from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    '''Extending the user model by a profile, used the tutorials:

    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

    https://dev.to/earthcomfy/django-user-profile-3hik
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    location = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.username
