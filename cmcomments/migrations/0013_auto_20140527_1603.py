# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0012_auto_20140527_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='stage',
            field=models.SmallIntegerField(default=2, choices=[(0, 'inspiration'), (1, 'plan'), (2, 'build'), (3, 'test'), (4, 'reflect')]),
        ),
    ]
