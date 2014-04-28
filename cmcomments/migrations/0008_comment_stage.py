# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0007_comment_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='stage',
            field=models.SmallIntegerField(choices=[(1, 'Plan'), (2, 'Build'), (3, 'Test')], default=2),
            preserve_default=True,
        ),
    ]
