# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_auto_20150108_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='about_me_image',
            field=models.ForeignKey(null=True, blank=True, to_field='id', on_delete=django.db.models.deletion.SET_NULL, to='images.Image'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_me_video',
            field=models.ForeignKey(null=True, blank=True, to_field='id', on_delete=django.db.models.deletion.SET_NULL, to='videos.Video'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_research_video',
            field=models.ForeignKey(null=True, blank=True, to_field='id', on_delete=django.db.models.deletion.SET_NULL, to='videos.Video'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_research_image',
            field=models.ForeignKey(null=True, blank=True, to_field='id', on_delete=django.db.models.deletion.SET_NULL, to='images.Image'),
            preserve_default=True,
        ),
    ]
