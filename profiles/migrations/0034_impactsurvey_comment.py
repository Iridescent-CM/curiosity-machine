# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0033_auto_20170811_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='impactsurvey',
            name='comment',
            field=models.TextField(blank=True, default=''),
        ),
    ]
