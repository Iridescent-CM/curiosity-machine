# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-13 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0021_auto_20171207_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberlimit',
            name='role',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent'), (5, 'family')], default=0),
        ),
    ]
