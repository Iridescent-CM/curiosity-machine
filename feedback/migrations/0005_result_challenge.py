# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-03 17:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0059_auto_20180315_1519'),
        ('feedback', '0004_auto_20180503_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='challenge',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='challenges.Challenge'),
            preserve_default=False,
        ),
    ]
