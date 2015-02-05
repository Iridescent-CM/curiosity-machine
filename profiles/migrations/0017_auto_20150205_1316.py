# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0016_profile_expertise'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='shown_intro',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_me_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='about_me_image', to='images.Image'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_me_video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='about_me_video', to='videos.Video'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_research_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='about_research_image', to='images.Image'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_research_video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='about_research_video', to='videos.Video'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile'),
            preserve_default=True,
        ),
    ]
