# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0030_auto_20150211_0338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='theme',
        ),
        migrations.AlterField(
            model_name='challenge',
            name='themes',
            field=models.ManyToManyField(blank=True, to='challenges.Theme', null=True),
            preserve_default=True,
        ),
    ]
