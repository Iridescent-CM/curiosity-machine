# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-27 21:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hellosign', '0002_auto_20180124_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='signature',
            name='signature_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='signature_request_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
