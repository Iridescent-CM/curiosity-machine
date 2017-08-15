# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0015_auto_20170814_1117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='read',
        ),
    ]
