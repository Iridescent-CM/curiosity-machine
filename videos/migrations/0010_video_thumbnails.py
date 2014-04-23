# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0009_auto_20140423_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnails',
            field=models.ManyToManyField(blank=True, to='images.Image', null=True),
            preserve_default=True,
        ),
    ]
