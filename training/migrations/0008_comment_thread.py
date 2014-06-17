# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0007_comment_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='thread',
            field=models.ForeignKey(null=True, to_field='id', blank=True, to='training.Comment'),
            preserve_default=True,
        ),
    ]
