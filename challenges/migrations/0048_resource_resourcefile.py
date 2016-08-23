# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_s3_storage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0047_challenge_free'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('challenge', models.ForeignKey(null=True, to='challenges.Challenge')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(storage=django_s3_storage.storage.S3Storage(aws_s3_metadata={'Content-Disposition': 'attachment'}), upload_to='challenge_resource/%Y/%m/%d/')),
                ('link_text', models.CharField(null=True, max_length=64)),
                ('resource', models.ForeignKey(to='challenges.Resource')),
            ],
        ),
    ]
