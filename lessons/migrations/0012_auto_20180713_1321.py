# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-13 20:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0011_lesson_quiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={'verbose_name_plural': 'Quizzes'},
        ),
        migrations.AddField(
            model_name='comment',
            name='role',
            field=models.CharField(default='comment', max_length=50),
        ),
    ]
