# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0008_comment_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='stage',
            field=models.SmallIntegerField(default=2, choices=[(1, 'plan'), (2, 'build'), (3, 'test')]),
        ),
    ]
