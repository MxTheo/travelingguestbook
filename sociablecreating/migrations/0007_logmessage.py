# Generated by Django 5.0.4 on 2024-04-23 10:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociablecreating', '0006_rename_search_code_networker_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Anonymous', max_length=70, verbose_name='Your name')),
                ('body', models.CharField(max_length=300)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('networker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sociablecreating.networker')),
            ],
            options={
                'ordering': ['-date_modified', '-date_created'],
            },
        ),
    ]
