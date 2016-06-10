# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_s3_storage.storage
import memberships.models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0008_memberimport'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberimport',
            name='output',
            field=models.FileField(blank=True, storage=django_s3_storage.storage.S3Storage(), null=True, upload_to='memberships/imports/'),
        ),
        migrations.AddField(
            model_name='memberimport',
            name='success',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='memberimport',
            name='input',
            field=models.FileField(storage=django_s3_storage.storage.S3Storage(), validators=[memberships.models.member_import_csv_validator], upload_to='memberships/imports/'),
        ),
    ]
