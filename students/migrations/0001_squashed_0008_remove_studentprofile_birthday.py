# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-28 20:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('students', '0001_initial'), ('students', '0002_auto_20171103_0806'), ('students', '0003_auto_20171106_0849'), ('students', '0004_auto_20171106_0938'), ('students', '0005_auto_20171107_1731'), ('students', '0006_studentprofile_full_access'), ('students', '0007_auto_20180126_1127'), ('students', '0008_remove_studentprofile_birthday')]

    initial = True

    dependencies = [
        ('profiles', '0037_auto_20171103_0807'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('images', '0003_auto_20140421_1526'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_first_name', models.TextField(blank=True)),
                ('parent_last_name', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='studentprofile', to=settings.AUTH_USER_MODEL)),
                ('city', models.TextField(blank=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image')),
                ('full_access', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]