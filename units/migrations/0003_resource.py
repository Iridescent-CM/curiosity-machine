# encoding: utf8
from django.db import models, migrations
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0002_unit_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('link_text', models.CharField(max_length=128)),
                ('file', s3direct.fields.S3DirectField(null=True, blank=True, help_text='Uploads will overwrite files of the same name')),
                ('units', models.ManyToManyField(null=True, blank=True, to='units.Unit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
