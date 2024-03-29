# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-11-20 16:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('families', '0001_initial'), ('families', '0002_familymember'), ('families', '0003_familymember_image'), ('families', '0004_auto_20180130_1947'), ('families', '0005_auto_20180201_1249'), ('families', '0006_auto_20180208_0822'), ('families', '0007_auto_20180306_1114'), ('families', '0008_auto_20180315_1519'), ('families', '0009_auto_20180315_1350'), ('families', '0010_auto_20180503_1143'), ('families', '0011_auto_20180815_1528'), ('families', '0012_familyprofile_awardforce_slug'), ('families', '0013_familyprofile_members_confirmed'), ('families', '0014_familyprofile_awardforce_email'), ('families', '0015_auto_20181031_1341'), ('families', '0016_remove_familymember_birthday'), ('families', '0017_awardforceintegration_last_used'), ('families', '0018_permissionslip'), ('families', '0019_auto_20181129_1135'), ('families', '0020_remove_familyprofile_phone')]

    initial = True

    dependencies = [
        ('images', '0003_auto_20140421_1526'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hellosign', '0003_auto_20180227_1318'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.Location')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='familyprofile', to=settings.AUTH_USER_MODEL)),
                ('welcomed', models.DateTimeField(blank=True, null=True)),
                ('members_confirmed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FamilyMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('family_role', models.SmallIntegerField(choices=[(None, 'Select role...'), (0, 'Parent or guardian'), (1, 'Child')])),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image')),
            ],
        ),
        migrations.CreateModel(
            name='AwardForceIntegration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=16, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('last_used', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PermissionSlip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
