# encoding: utf8
from django.db import models, migrations
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0002_unit_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='lesson_plan',
            field=s3direct.fields.S3DirectField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unit',
            name='workbook',
            field=s3direct.fields.S3DirectField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
