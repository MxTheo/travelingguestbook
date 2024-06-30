from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Goal(models.Model):
    '''A goal is given to a sociable,
    so that the receiver knows what to do with it'''
    title        = models.CharField(max_length=150)
    nr_chosen    = models.IntegerField("number of times the goal was chosen" , editable=False, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    creator      = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-nr_chosen', '-date_created']

    def get_absolute_url(self):
        '''Directs towards the detail page'''
        return reverse("goal", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return str(self.title)
