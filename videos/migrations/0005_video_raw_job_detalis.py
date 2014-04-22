# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0004_video_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='raw_job_detalis',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
