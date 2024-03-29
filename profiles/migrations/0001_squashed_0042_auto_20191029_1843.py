# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-28 20:04
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('profiles', '0001_initial'), ('profiles', '0002_auto_20140317_1718'), ('profiles', '0003_auto_20140320_1335'), ('profiles', '0004_auto_20140324_1601'), ('profiles', '0005_profile_image'), ('profiles', '0006_auto_20140513_0919'), ('profiles', '0007_profile_approved'), ('profiles', '0008_remove_profile_nickname'), ('profiles', '0009_profile_last_active_on'), ('profiles', '0010_profile_last_inactive_email_sent_on'), ('profiles', '0011_auto_20141210_1442'), ('profiles', '0012_profile_is_student'), ('profiles', '0013_auto_20141216_1041'), ('profiles', '0014_auto_20150108_1044'), ('profiles', '0015_auto_20150120_0934'), ('profiles', '0016_profile_expertise'), ('profiles', '0017_profile_is_educator'), ('profiles', '0018_auto_20150205_1316'), ('profiles', '0019_profile_is_parent'), ('profiles', '0020_auto_20150518_1354'), ('profiles', '0021_parentconnection_retries'), ('profiles', '0022_auto_20150629_1300'), ('profiles', '0023_profile_source'), ('profiles', '0024_auto_20151117_1605'), ('profiles', '0025_auto_20151117_1606'), ('profiles', '0026_profile_first_login'), ('profiles', '0027_auto_20160324_1346'), ('profiles', '0028_auto_20160506_1138'), ('profiles', '0029_profile_role'), ('profiles', '0030_auto_20160512_1407'), ('profiles', '0031_auto_20160512_1452'), ('profiles', '0032_impactsurvey'), ('profiles', '0033_auto_20170811_1221'), ('profiles', '0034_impactsurvey_comment'), ('profiles', '0035_profile_organization'), ('profiles', '0036_userextra'), ('profiles', '0037_auto_20171103_0807'), ('profiles', '0038_auto_20171103_0842'), ('profiles', '0039_user'), ('profiles', '0040_auto_20180126_1412'), ('profiles', '0041_auto_20180208_0822'), ('profiles', '0042_auto_20191029_1843')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('images', '__first__'),
        ('auth', '0008_alter_user_username_max_length'),
        ('videos', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpactSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_count', models.PositiveIntegerField(blank=True, default=0)),
                ('teacher_count', models.PositiveIntegerField(blank=True, default=0)),
                ('challenge_count', models.PositiveIntegerField(blank=True, default=0)),
                ('in_classroom', models.BooleanField(default=False)),
                ('out_of_classroom', models.BooleanField(default=False)),
                ('hours_per_challenge', models.PositiveIntegerField(blank=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('comment', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='UserExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.SmallIntegerField(choices=[(0, 'none'), (1, 'student'), (3, 'educator'), (5, 'family')], default=0)),
                ('source', models.CharField(blank=True, default='', max_length=50)),
                ('last_active_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_inactive_email_sent_on', models.DateTimeField(blank=True, default=None, null=True)),
                ('first_login', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extra', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
