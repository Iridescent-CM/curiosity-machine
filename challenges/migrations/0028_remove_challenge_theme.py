# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_auto_20150127_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='theme',
        ),
    ]
