# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0049_auto_20160919_1610'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='challenge',
            options={'ordering': ['order', '-id']},
        ),
        migrations.AddField(
            model_name='challenge',
            name='difficulty_level',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)], help_text='From 1 (easy) to 3 (difficult)', default=1),
        ),
    ]
