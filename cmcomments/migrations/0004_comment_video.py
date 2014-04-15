# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0003_comment_created'),
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(null=True, to_field='id', blank=True, to='videos.Video'),
            preserve_default=True,
        ),
    ]
