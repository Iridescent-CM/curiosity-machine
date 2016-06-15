# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0010_auto_20160614_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberimport',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 15, 1, 26, 23, 165567, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='memberimport',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 15, 1, 26, 29, 43891, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
