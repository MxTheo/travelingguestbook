# Generated by Django 5.0.4 on 2024-09-27 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0002_profile_custom_description_for_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lvl',
            field=models.IntegerField(default=0, verbose_name='level van de gebruiker'),
        ),
    ]
