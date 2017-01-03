# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0016_auto_20161019_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(verbose_name='Active', help_text='Designates whether a membership is considered active. Unselect this when a membership expires instead of deleting it.', default=True),
        ),
    ]
