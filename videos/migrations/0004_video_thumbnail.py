# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0003_auto_20140421_1525'),
        ('images', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnail',
            field=models.ForeignKey(blank=True, to='images.Image', null=True, to_field='id'),
            preserve_default=True,
        ),
    ]
