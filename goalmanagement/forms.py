from django.forms import ModelForm
from .models import Goal


class GoalForm(ModelForm):
    '''Form for the model Goal'''
    class Meta:
        model = Goal
        fields = ['title']
