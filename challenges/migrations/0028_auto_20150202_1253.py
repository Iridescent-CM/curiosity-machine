# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from challenges.models import Challenge
from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings

def theme2categories(apps, schema_editor):
   for challenge in Challenge.objects.all():
        challenge.categories = challenge.theme
        challenge.save()

class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_challenge_mentor_guide'),
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
        migrations.RemoveField(
            model_name='challenge',
            name='theme',
        ),
        migrations.AddField(
            model_name='challenge',
            name='categories',
            field=models.ManyToManyField(to='challenges.Theme', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='favorited',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, related_name='favorite_challenges', through='challenges.Favorite'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='students',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, related_name='challenges', through='challenges.Progress'),
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
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='mentored_progresses', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='progress',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='progresses'),
            preserve_default=True,
        ),
    ]
