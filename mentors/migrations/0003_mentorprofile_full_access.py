# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-26 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentors', '0002_auto_20171108_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorprofile',
            name='full_access',
            field=models.BooleanField(default=False),
        ),
    ]