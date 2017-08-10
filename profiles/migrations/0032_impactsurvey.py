# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0031_auto_20160512_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpactSurvey',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('student_count', models.PositiveIntegerField(default=0, blank=True)),
                ('teacher_count', models.PositiveIntegerField(default=0, blank=True)),
                ('challenge_count', models.PositiveIntegerField(default=0, blank=True)),
                ('in_classroom', models.BooleanField(default=False)),
                ('out_of_classroom', models.BooleanField(default=False)),
                ('hours_per_challenge', models.PositiveIntegerField(default=0, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
