# Generated by Django 5.2 on 2025-04-15 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
