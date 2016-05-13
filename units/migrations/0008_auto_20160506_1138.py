# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0007_auto_20150904_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='units',
            field=models.ManyToManyField(to='units.Unit', related_name='resources', blank=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='challenges',
            field=models.ManyToManyField(to='challenges.Challenge', blank=True, through='units.UnitChallenge'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='image',
            field=models.ForeignKey(null=True, related_name='image', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='unit',
            name='standards_alignment_image',
            field=models.ForeignKey(null=True, related_name='unit', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
