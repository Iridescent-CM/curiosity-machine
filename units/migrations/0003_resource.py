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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('unit', models.ForeignKey(to_field='id', to='units.Unit')),
                ('link_text', models.CharField(max_length=128)),
                ('file', s3direct.fields.S3DirectField(null=True, blank=True, help_text='Uploads will overwrite files of the same name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
