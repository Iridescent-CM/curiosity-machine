# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0028_auto_20160506_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.SmallIntegerField(default=0, choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent')]),
            preserve_default=True,
        ),
    ]
