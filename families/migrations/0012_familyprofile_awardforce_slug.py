# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-16 20:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0011_auto_20180815_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='familyprofile',
            name='awardforce_slug',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]