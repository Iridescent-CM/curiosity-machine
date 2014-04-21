# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0006_remove_comment_image'),
        ('images', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='image',
            field=models.ForeignKey(blank=True, to_field='id', null=True, to='images.Image'),
            preserve_default=True,
        ),
    ]
