# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import units.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0009_unit_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='slug',
            field=models.SlugField(blank=True, help_text='unit slug, allows accessing unit through alternate url, i.e. /units/{slug}', null=True, validators=[units.validators.validate_has_non_numeric]),
        ),
    ]
