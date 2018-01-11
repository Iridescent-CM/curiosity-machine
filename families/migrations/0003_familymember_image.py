# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-10 20:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20140421_1526'),
        ('families', '0002_familymember'),
    ]

    operations = [
        migrations.AddField(
            model_name='familymember',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image'),
        ),
    ]
