# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0008_video_thumbnails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='thumbnails',
        ),
        migrations.AlterField(
            model_name='video',
            name='raw_job_details',
            field=models.TextField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='encodedvideo',
            unique_together=set([('video', 'width', 'height', 'mime_type')]),
        ),
    ]
