# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='source_url',
            field=models.URLField(blank=True, default='', max_length=2048),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='image',
            name='filepicker_url',
        ),
    ]
