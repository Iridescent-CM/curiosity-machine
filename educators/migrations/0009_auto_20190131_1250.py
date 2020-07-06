# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-31 20:50
from __future__ import unicode_literals

import curiositymachine.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educators', '0008_auto_20180508_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educatorprofile',
            name='organization',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[curiositymachine.validators.validate_simple_latin]),
        ),
    ]