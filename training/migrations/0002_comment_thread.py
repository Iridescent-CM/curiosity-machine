# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='thread',
            field=models.ForeignKey(blank=True, to_field='id', null=True, to='training.Comment'),
            preserve_default=True,
        ),
    ]
