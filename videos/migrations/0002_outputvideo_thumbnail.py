# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='outputvideo',
            name='thumbnail',
            field=models.URLField(max_length=2083, blank=True, null=True),
            preserve_default=True,
        ),
    ]
