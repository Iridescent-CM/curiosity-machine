# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0004_auto_20160509_0953'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberLimit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('role', models.SmallIntegerField(default=0, choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent')])),
                ('limit', models.PositiveIntegerField(default=0, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='membership',
            name='educator_limit',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='student_limit',
        ),
        migrations.AlterField(
            model_name='membership',
            name='challenges',
            field=models.ManyToManyField(to='challenges.Challenge', blank=True),
        ),
        migrations.AlterField(
            model_name='membership',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='memberships.Member', blank=True),
        ),
        migrations.AddField(
            model_name='memberlimit',
            name='membership',
            field=models.ForeignKey(to='memberships.Membership'),
        ),
    ]
