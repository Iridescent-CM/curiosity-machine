# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0010_auto_20140430_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ForeignKey(to='images.Image', to_field='id', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(to='videos.Video', to_field='id', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
