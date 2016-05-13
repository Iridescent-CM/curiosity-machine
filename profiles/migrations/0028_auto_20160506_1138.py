# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0027_auto_20160324_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Educator',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('profiles.profile',),
        ),
        migrations.CreateModel(
            name='Mentor',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('profiles.profile',),
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('profiles.profile',),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('profiles.profile',),
        ),
        migrations.AlterField(
            model_name='parentconnection',
            name='child_profile',
            field=models.ForeignKey(to='profiles.Profile', related_name='connections_as_child'),
        ),
        migrations.AlterField(
            model_name='parentconnection',
            name='parent_profile',
            field=models.ForeignKey(to='profiles.Profile', related_name='connections_as_parent'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_me_image',
            field=models.ForeignKey(null=True, related_name='about_me_image', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_me_video',
            field=models.ForeignKey(null=True, related_name='about_me_video', blank=True, to='videos.Video', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_research_image',
            field=models.ForeignKey(null=True, related_name='about_research_image', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about_research_video',
            field=models.ForeignKey(null=True, related_name='about_research_video', blank=True, to='videos.Video', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='child_profiles',
            field=models.ManyToManyField(to='profiles.Profile', related_name='parent_profiles', through='profiles.ParentConnection'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
