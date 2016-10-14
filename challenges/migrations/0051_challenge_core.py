# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0050_auto_20160926_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='core',
            field=models.BooleanField(help_text='Core challenges are considered part of the core offering for non-membership users', default=False),
        ),
    ]
