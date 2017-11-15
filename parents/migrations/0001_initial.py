# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-07 19:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('images', '0003_auto_20140421_1526'),
        ('students', '0004_auto_20171106_0938'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('removed', models.BooleanField(default=False)),
                ('retries', models.PositiveSmallIntegerField(default=0)),
                ('child_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections_as_child', to='students.StudentProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ParentProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.TextField(blank=True)),
                ('child_profiles', models.ManyToManyField(related_name='parent_profiles', through='parents.ParentConnection', to='students.StudentProfile')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parentprofile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='parentconnection',
            name='parent_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections_as_parent', to='parents.ParentProfile'),
        ),
    ]
