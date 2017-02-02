# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0017_membership_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='memberships.Group')),
                ('member', models.ForeignKey(to='memberships.Member')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(through='memberships.GroupMember', blank=True, to='memberships.Member'),
        ),
        migrations.AddField(
            model_name='group',
            name='membership',
            field=models.ForeignKey(to='memberships.Membership'),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('membership', 'name')]),
        ),
    ]
