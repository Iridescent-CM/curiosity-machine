# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-31 03:47
from __future__ import unicode_literals

from django.db import migrations, models
import families.models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0003_familymember_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familymember',
            name='family_role',
            field=models.SmallIntegerField(choices=[(None, 'Select role...'), (0, families.models.FamilyRole.display), (1, families.models.FamilyRole.display)]),
        ),
    ]
