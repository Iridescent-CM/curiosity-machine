# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-28 16:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0008_auto_20180618_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='start',
            field=models.TextField(blank=True),
        ),
    ]
