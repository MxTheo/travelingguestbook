# Generated by Django 5.0.4 on 2024-09-22 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociablecreating', '0005_alter_logmessage_body_alter_sociable_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='logmessage',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='is gelezen'),
        ),
    ]
