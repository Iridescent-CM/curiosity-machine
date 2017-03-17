# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_auto_20170317_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='answer_1',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]),
        ),
        migrations.AlterField(
            model_name='result',
            name='answer_2',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]),
        ),
        migrations.AlterField(
            model_name='result',
            name='answer_3',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]),
        ),
        migrations.AlterField(
            model_name='result',
            name='answer_4',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]),
        ),
    ]
