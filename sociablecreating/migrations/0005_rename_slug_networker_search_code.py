# Generated by Django 5.0.4 on 2024-04-19 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sociablecreating', '0004_rename_search_code_networker_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='networker',
            old_name='slug',
            new_name='search_code',
        ),
    ]
