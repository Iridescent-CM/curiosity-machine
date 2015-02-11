# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0028_auto_20150203_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='themes',
            field=models.ManyToManyField(null=True, related_name='challenges', to='challenges.Theme', blank=True),
            preserve_default=True,
        ),
    ]
