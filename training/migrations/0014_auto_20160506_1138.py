# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0013_task_completion_email_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ForeignKey(null=True, related_name='mentor_training_comments', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='task',
            field=models.ForeignKey(to='training.Task', related_name='comments'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='thread',
            field=models.ForeignKey(null=True, related_name='replies', blank=True, to='training.Comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='mentor_training_comments'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(null=True, related_name='mentor_training_comments', blank=True, to='videos.Video', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='module',
            name='image',
            field=models.ForeignKey(null=True, related_name='modules', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='task',
            name='image',
            field=models.ForeignKey(null=True, related_name='tasks', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='task',
            name='mentors_done',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='completed_tasks', blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='module',
            field=models.ForeignKey(to='training.Module', related_name='tasks'),
        ),
    ]
