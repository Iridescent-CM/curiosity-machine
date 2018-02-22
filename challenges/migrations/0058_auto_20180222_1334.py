# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-22 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0057_auto_20180209_1012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filter',
            name='color',
        ),
        migrations.RemoveField(
            model_name='theme',
            name='color',
        ),
        migrations.AlterField(
            model_name='filter',
            name='name',
            field=models.CharField(help_text='name of the filter', max_length=100),
        ),
    ]