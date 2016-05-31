# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0005_auto_20160517_2231'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='memberlimit',
            unique_together=set([('role', 'membership')]),
        ),
    ]
