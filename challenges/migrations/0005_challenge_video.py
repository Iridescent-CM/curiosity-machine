# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0004_auto_20140403_0954'),
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='video',
            field=models.ForeignKey(to_field='id', to='videos.Video', null=True, blank=True),
            preserve_default=True,
        ),
    ]
