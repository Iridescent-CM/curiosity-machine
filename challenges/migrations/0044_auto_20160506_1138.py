# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0043_auto_20160317_1155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='progress',
            options={'verbose_name_plural': 'progresses'},
        ),
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='challenge',
            name='favorited',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='favorite_challenges', through='challenges.Favorite'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='reflect_questions',
            field=models.ManyToManyField(to='challenges.Question'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='students',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='challenges', through='challenges.Progress'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='themes',
            field=models.ManyToManyField(to='challenges.Theme', related_name='challenges', blank=True),
        ),
        migrations.AlterField(
            model_name='example',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='example',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorites'),
        ),
        migrations.AlterField(
            model_name='filter',
            name='challenges',
            field=models.ManyToManyField(to='challenges.Challenge', related_name='filters'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='mentor',
            field=models.ForeignKey(null=True, related_name='mentored_progresses', blank=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='progress',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='progresses'),
        ),
    ]
