# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0013_auto_20140527_1603'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='comment',
            name='challenge_progress',
            field=models.ForeignKey(to='challenges.Progress', related_name='comments'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ForeignKey(null=True, related_name='comments', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(null=True, related_name='comments', blank=True, to='videos.Video', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
