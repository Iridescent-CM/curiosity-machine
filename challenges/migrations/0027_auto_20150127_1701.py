# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0026_auto_20140630_0708'),
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
        migrations.AddField(
            model_name='challenge',
            name='categories',
            field=models.ManyToManyField(null=True, to='challenges.Theme', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='favorited',
            field=models.ManyToManyField(null=True, related_name='favorite_challenges', to=settings.AUTH_USER_MODEL, through='challenges.Favorite'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='students',
            field=models.ManyToManyField(null=True, related_name='challenges', to=settings.AUTH_USER_MODEL, through='challenges.Progress'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='theme',
            field=models.ForeignKey(to='challenges.Theme', related_name='challenge_theme', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='favorite',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorites'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='progress',
            name='mentor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='mentored_progresses', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='progress',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='progresses'),
            preserve_default=True,
        ),
    ]
