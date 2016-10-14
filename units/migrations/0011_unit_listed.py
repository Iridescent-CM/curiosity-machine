# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0010_auto_20161007_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='listed',
            field=models.BooleanField(help_text='This unit should be visible in the units listing for all users', default=False),
        ),
    ]
