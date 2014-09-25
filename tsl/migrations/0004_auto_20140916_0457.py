# encoding: utf8
from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tsl', '0003_auto_20140915_0612'),
        ('images', '__first__'),
        ('videos', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='video',
            field=models.ForeignKey(blank=True, to='videos.Video', to_field='id', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='image',
            field=models.ForeignKey(blank=True, to='images.Image', to_field='id', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
