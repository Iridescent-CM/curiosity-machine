# encoding: utf8
from django.db import models, migrations
from images.models import Image
from videos.models import Video
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '__first__'),
        ('images', '__first__'),
        ('profiles', '0011_auto_20141210_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='about_research_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='images.Image', to_field='id', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_me_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='images.Image', to_field='id', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_research_video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='videos.Video', to_field='id', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_me_video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='videos.Video', to_field='id', null=True),
            preserve_default=True,
        ),
    ]
