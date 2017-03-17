# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='answer_1_1',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_1_2',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_1_3',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_1_4',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_1_5',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_1_6',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_2_1',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_2_2',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_2_3',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_2_4',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_2_5',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_2_6',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_3_1',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_3_2',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_3_3',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_3_4',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_3_5',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_3_6',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_4_1',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_4_2',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_4_3',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_4_4',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_4_5',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answer_4_6',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='correct_answer_1',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)], blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='correct_answer_2',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)], blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='correct_answer_3',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)], blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='correct_answer_4',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)], blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='question_1',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='question_2',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='question_3',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='question_4',
            field=models.TextField(null=True, blank=True),
        ),
    ]
