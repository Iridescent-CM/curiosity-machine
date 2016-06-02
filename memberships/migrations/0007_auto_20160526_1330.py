# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0006_auto_20160524_1415'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('membership', 'user')]),
        ),
    ]
