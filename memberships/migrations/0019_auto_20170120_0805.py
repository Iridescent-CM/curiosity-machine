# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0018_auto_20170110_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 1, 20, 16, 5, 33, 675341, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 20, 16, 5, 38, 547360, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 1, 20, 16, 5, 42, 651499, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membership',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 20, 16, 5, 46, 203397, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
