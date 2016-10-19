# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0015_auto_20161007_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='challenges',
            field=models.ManyToManyField(to='challenges.Challenge', blank=True, help_text='Users who are part of this membership will have access to the selected Challenges.'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='extra_units',
            field=models.ManyToManyField(to='units.Unit', blank=True, help_text='Users who are part of this membership will have access to these units in addition to the standard listed units.'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='name',
            field=models.CharField(max_length=255, unique=True, help_text='Use this format: State-School Name-School Level-Grade Level e.g. “CA-Magnolia-ES-3”.'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='notes',
            field=models.TextField(null=True, blank=True, help_text='Internal team notes that will not be displayed to users. Use this space to record information about a membership that doesn’t fit into other fields but is important for the team to know.'),
        ),
    ]
