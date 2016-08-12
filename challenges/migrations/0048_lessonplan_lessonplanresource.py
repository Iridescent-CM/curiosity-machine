# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0047_challenge_free'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('challenge', models.ForeignKey(null=True, to='challenges.Challenge')),
            ],
        ),
        migrations.CreateModel(
            name='LessonPlanResource',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='lesson_plan/%Y/%m/%d/')),
                ('link_text', models.CharField(null=True, max_length=64)),
                ('lesson_plan', models.ForeignKey(to='challenges.LessonPlan')),
            ],
        ),
    ]
