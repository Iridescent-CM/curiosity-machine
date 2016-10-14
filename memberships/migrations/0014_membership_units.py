# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0008_auto_20160506_1138'),
        ('memberships', '0013_auto_20160822_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='units',
            field=models.ManyToManyField(blank=True, to='units.Unit'),
        ),
    ]
