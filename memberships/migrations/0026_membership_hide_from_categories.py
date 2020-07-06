# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-19 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0025_auto_20180201_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='hide_from_categories',
            field=models.BooleanField(default=False, help_text="Select this option if you don't want the membership to show up on the main challenges page for its members."),
        ),
    ]