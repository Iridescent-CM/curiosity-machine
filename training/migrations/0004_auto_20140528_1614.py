# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_module_mentors_done'),
        ('images', '__first__'),
        ('videos', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(to_field='id', null=True, to='videos.Video', blank=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='image',
            field=models.ForeignKey(to_field='id', null=True, to='images.Image', blank=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
