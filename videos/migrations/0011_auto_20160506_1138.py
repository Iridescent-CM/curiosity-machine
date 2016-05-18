# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0010_video_thumbnails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encodedvideo',
            name='video',
            field=models.ForeignKey(to='videos.Video', related_name='encoded_videos'),
        ),
        migrations.AlterField(
            model_name='video',
            name='thumbnails',
            field=models.ManyToManyField(to='images.Image', blank=True),
        ),
    ]
