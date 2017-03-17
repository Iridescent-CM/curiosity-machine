# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0052_auto_20161019_1503'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False, help_text='Enable this option to show this quiz to students')),
                ('question_1', models.TextField()),
                ('answer_1_1', models.TextField()),
                ('answer_1_2', models.TextField()),
                ('answer_1_3', models.TextField()),
                ('answer_1_4', models.TextField()),
                ('answer_1_5', models.TextField()),
                ('answer_1_6', models.TextField()),
                ('correct_answer_1', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('question_2', models.TextField()),
                ('answer_2_1', models.TextField()),
                ('answer_2_2', models.TextField()),
                ('answer_2_3', models.TextField()),
                ('answer_2_4', models.TextField()),
                ('answer_2_5', models.TextField()),
                ('answer_2_6', models.TextField()),
                ('correct_answer_2', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('question_3', models.TextField()),
                ('answer_3_1', models.TextField()),
                ('answer_3_2', models.TextField()),
                ('answer_3_3', models.TextField()),
                ('answer_3_4', models.TextField()),
                ('answer_3_5', models.TextField()),
                ('answer_3_6', models.TextField()),
                ('correct_answer_3', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('question_4', models.TextField()),
                ('answer_4_1', models.TextField()),
                ('answer_4_2', models.TextField()),
                ('answer_4_3', models.TextField()),
                ('answer_4_4', models.TextField()),
                ('answer_4_5', models.TextField()),
                ('answer_4_6', models.TextField()),
                ('correct_answer_4', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('challenge', models.ForeignKey(to='challenges.Challenge')),
            ],
            options={
                'verbose_name_plural': 'Quizzes',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('answer_1', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('answer_2', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('answer_3', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('answer_4', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('quiz', models.ForeignKey(to='quizzes.Quiz')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
