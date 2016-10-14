# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import units.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0008_auto_20160506_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='slug',
            field=models.SlugField(null=True, help_text='unit slug, allows accessing unit through alternate url, i.e. /units/<slug>', validators=[units.validators.validate_has_non_numeric], blank=True),
        ),
    ]
