# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-28 16:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('cmcomments', '0001_initial'), ('cmcomments', '0002_comment_image'), ('cmcomments', '0003_comment_created'), ('cmcomments', '0004_comment_video'), ('cmcomments', '0005_comment_read'), ('cmcomments', '0006_remove_comment_image'), ('cmcomments', '0007_comment_image'), ('cmcomments', '0008_comment_stage'), ('cmcomments', '0009_auto_20140428_1344'), ('cmcomments', '0010_auto_20140430_1444'), ('cmcomments', '0011_auto_20140501_1501'), ('cmcomments', '0012_auto_20140527_1436'), ('cmcomments', '0013_auto_20140527_1603'), ('cmcomments', '0014_auto_20160506_1138'), ('cmcomments', '0015_auto_20170814_1117'), ('cmcomments', '0016_remove_comment_read')]

    initial = True

    dependencies = [
        ('notifications', '0005_auto_20160504_1520'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('challenges', '0002_auto_20140325_1620'),
        ('images', '__first__'),
        ('videos', '0001_initial'),
        ('challenges', '0006_auto_20140423_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='challenges.Progress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='id')),
                ('text', models.TextField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='videos.Video')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='images.Image')),
                ('stage', models.SmallIntegerField(choices=[(0, 'inspiration'), (1, 'plan'), (2, 'build'), (3, 'test'), (4, 'reflect')], default=2)),
                ('question_text', models.TextField(default='', help_text='If the comment is in direct reply to a question, this will contain the full text of the question.')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]
