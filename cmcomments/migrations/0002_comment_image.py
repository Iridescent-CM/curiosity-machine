# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='image',
            field=models.URLField(null=True, max_length=2083, blank=True),
            preserve_default=True,
        ),
    ]
