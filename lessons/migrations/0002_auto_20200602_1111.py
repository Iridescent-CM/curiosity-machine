# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-06-02 18:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_squashed_0017_auto_20190314_0901-1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lessons.Lesson'),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lessons.Quiz'),
        ),
    ]
