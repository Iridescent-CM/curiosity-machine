# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0007_remove_video_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnails',
            field=models.ManyToManyField(null=True, to='images.Image'),
            preserve_default=True,
        ),
    ]
