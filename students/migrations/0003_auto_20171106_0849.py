# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 16:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_auto_20171103_0806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='birthday',
            field=models.DateField(null=True),
        ),
    ]
