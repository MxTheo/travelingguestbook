# Generated by Django 5.0.4 on 2024-04-19 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociablecreating', '0002_alter_networker_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networker',
            name='search_code',
            field=models.SlugField(editable=False, max_length=8, unique=True, verbose_name='Code used to find the networker'),
        ),
    ]
