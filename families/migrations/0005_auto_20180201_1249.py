# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-01 20:49
from __future__ import unicode_literals

from django.db import migrations, models
import families.models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0004_auto_20180130_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='familyprofile',
            name='welcomed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='family_role',
            field=models.SmallIntegerField(choices=[(None, 'Select role...'), (0, families.models.FamilyRole.display), (1, families.models.FamilyRole.display)]),
        ),
    ]
