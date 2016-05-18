# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0044_challenge_landing_image'),
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
            field=models.ManyToManyField(related_name='favorite_challenges', to=settings.AUTH_USER_MODEL, through='challenges.Favorite'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='landing_image',
            field=models.ForeignKey(null=True, help_text='Image size should be a 4:3 ratio, at least 720px wide for best results. Jpg, png, or gif accepted.', related_name='+', blank=True, on_delete=django.db.models.deletion.PROTECT, to='images.Image'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='reflect_questions',
            field=models.ManyToManyField(to='challenges.Question'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='students',
            field=models.ManyToManyField(related_name='challenges', to=settings.AUTH_USER_MODEL, through='challenges.Progress'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='themes',
            field=models.ManyToManyField(related_name='challenges', to='challenges.Theme', blank=True),
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
            field=models.ForeignKey(related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='filter',
            name='challenges',
            field=models.ManyToManyField(related_name='filters', to='challenges.Challenge'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='mentor',
            field=models.ForeignKey(null=True, related_name='mentored_progresses', blank=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='progress',
            name='student',
            field=models.ForeignKey(related_name='progresses', to=settings.AUTH_USER_MODEL),
        ),
    ]
