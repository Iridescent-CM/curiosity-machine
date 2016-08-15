# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0045_auto_20160513_1009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='public',
        ),
    ]
