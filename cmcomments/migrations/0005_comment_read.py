# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0004_comment_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='read',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
