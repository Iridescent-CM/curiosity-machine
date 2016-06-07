# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_s3_storage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0007_auto_20160526_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('input', models.FileField(upload_to='', storage=django_s3_storage.storage.S3Storage(aws_s3_key_prefix='memberships/imports/'))),
                ('membership', models.ForeignKey(to='memberships.Membership')),
            ],
        ),
    ]
