# Generated by Django 5.0.4 on 2024-05-06 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goalmanagement', '0002_alter_goal_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='nr_chosen',
            field=models.IntegerField(default=0, editable=False, verbose_name='number of times the goal was chosen'),
        ),
    ]
