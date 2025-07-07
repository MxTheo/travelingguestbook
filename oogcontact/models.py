from django.db import models

class Registration(models.Model):
    '''Model to store registration details for the course.'''
    number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)
    hasCanceled = models.BooleanField(default=False)

    def __str__(self):
        return self.name
