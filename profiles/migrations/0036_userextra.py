# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-03 15:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0035_profile_organization'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.SmallIntegerField(choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent')], default=0)),
                ('source', models.CharField(blank=True, default='', max_length=50)),
                ('approved', models.BooleanField(default=False)),
                ('last_active_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_inactive_email_sent_on', models.DateTimeField(blank=True, default=None, null=True)),
                ('first_login', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extra', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]