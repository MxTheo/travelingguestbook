# Generated by Django 5.1.3 on 2024-12-19 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociablecreating', '0016_alter_logmessage_body_alter_logmessage_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='sociable',
            name='number',
            field=models.IntegerField(default=0, verbose_name='Het nummer dat het aantal gecreeerd per user geeft'),
        ),
    ]