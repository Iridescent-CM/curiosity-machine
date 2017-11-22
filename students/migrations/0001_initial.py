# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-03 02:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('images', '0003_auto_20140421_1526'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.SmallIntegerField(choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent')], default=0)),
                ('source', models.CharField(blank=True, default='', max_length=50)),
                ('approved', models.BooleanField(default=False)),
                ('last_active_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_inactive_email_sent_on', models.DateTimeField(blank=True, default=None, null=True)),
                ('first_login', models.BooleanField(default=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('parent_first_name', models.TextField(blank=True)),
                ('parent_last_name', models.TextField(blank=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='studentprofile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]