# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-28 20:11
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import memberships.models
import memberships.validators
import re


class Migration(migrations.Migration):

    replaces = [('memberships', '0001_initial'), ('memberships', '0002_membership'), ('memberships', '0003_member_membership'), ('memberships', '0004_auto_20160509_0953'), ('memberships', '0005_auto_20160517_2231'), ('memberships', '0006_auto_20160524_1415'), ('memberships', '0007_auto_20160526_1330'), ('memberships', '0008_memberimport'), ('memberships', '0009_membership_display_name'), ('memberships', '0010_auto_20160819_1526'), ('memberships', '0011_auto_20160819_1537'), ('memberships', '0012_auto_20160822_1351'), ('memberships', '0013_auto_20160822_1408'), ('memberships', '0014_membership_units'), ('memberships', '0015_auto_20161007_1400'), ('memberships', '0016_auto_20161019_1503'), ('memberships', '0017_membership_is_active'), ('memberships', '0018_auto_20170110_1152'), ('memberships', '0019_auto_20170120_0805'), ('memberships', '0020_auto_20170227_1139'), ('memberships', '0021_auto_20171207_1446'), ('memberships', '0022_membership_slug'), ('memberships', '0023_auto_20171213_1123'), ('memberships', '0024_auto_20180131_0648'), ('memberships', '0025_auto_20180201_1249'), ('memberships', '0026_membership_hide_from_categories')]

    initial = True

    dependencies = [
        ('auth', '__first__'),
        ('challenges', '__first__'),
        ('units', '0008_auto_20160506_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='id')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('expiration', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('challenges', models.ManyToManyField(blank=True, to='challenges.Challenge')),
                ('members', models.ManyToManyField(blank=True, through='memberships.Member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='membership',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.Membership', to_field='id'),
        ),
        migrations.CreateModel(
            name='MemberLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.SmallIntegerField(choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent')], default=0)),
                ('limit', models.PositiveIntegerField(blank=True, default=0)),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.Membership')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='memberlimit',
            unique_together=set([('role', 'membership')]),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('membership', 'user')]),
        ),
        migrations.CreateModel(
            name='MemberImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input', models.FileField(help_text='Input file must be csv format, utf-8 encoding', upload_to=memberships.models.member_import_path, validators=[memberships.validators.member_import_csv_validator])),
                ('output', models.FileField(blank=True, null=True, upload_to=memberships.models.member_import_path)),
                ('status', models.SmallIntegerField(blank=True, choices=[(0, 'invalid'), (1, 'saved'), (2, 'unsaved'), (3, 'exception')], null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.Membership')),
            ],
        ),
        migrations.AddField(
            model_name='membership',
            name='display_name',
            field=models.CharField(help_text='The membership name users will see on the site (max 26 characters).', max_length=26),
        ),
        migrations.AddField(
            model_name='membership',
            name='extra_units',
            field=models.ManyToManyField(blank=True, help_text='Users who are part of this membership will have access to these units in addition to the standard listed units.', to='units.Unit'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='challenges',
            field=models.ManyToManyField(blank=True, help_text='Users who are part of this membership will have access to the selected Challenges.', to='challenges.Challenge'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='name',
            field=models.CharField(help_text='Use this format: State-School Name-School Level-Grade Level e.g. “CA-Magnolia-ES-3”.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='membership',
            name='notes',
            field=models.TextField(blank=True, help_text='Internal team notes that will not be displayed to users. Use this space to record information about a membership that doesn’t fit into other fields but is important for the team to know.', null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether a membership is considered active. Unselect this when a membership expires instead of deleting it. To restore an inactive membership, enable this and update the expiration date.', verbose_name='Active'),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.Group')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.Member')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, through='memberships.GroupMember', to='memberships.Member'),
        ),
        migrations.AddField(
            model_name='group',
            name='membership',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.Membership'),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('membership', 'name')]),
        ),
        migrations.AddField(
            model_name='member',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 1, 20, 16, 5, 33, 675341, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 1, 20, 16, 5, 38, 547360, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 1, 20, 16, 5, 42, 651499, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membership',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 1, 20, 16, 5, 46, 203397, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='membership',
            name='expiration',
            field=models.DateField(blank=True, help_text='Expired memberships will be automatically made inactive.', null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name='membership',
            name='slug',
            field=models.SlugField(blank=True, help_text='If provided, users can sign up for this membership at the slug url', null=True, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9_]+\\Z', 32), "Enter a valid 'slug' consisting of lowercase letters, numbers, underscores or hyphens.", 'invalid')]),
        ),
        migrations.AlterField(
            model_name='memberlimit',
            name='role',
            field=models.SmallIntegerField(choices=[(0, 'none'), (1, 'student'), (2, 'mentor'), (3, 'educator'), (4, 'parent'), (5, 'family')], default=0),
        ),
        migrations.AddField(
            model_name='membership',
            name='hide_from_categories',
            field=models.BooleanField(default=False, help_text="Select this option if you don't want the membership to show up on the main challenges page for its members."),
        ),
    ]
