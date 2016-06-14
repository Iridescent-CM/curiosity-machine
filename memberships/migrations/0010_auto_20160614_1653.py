# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import memberships.validators


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0009_auto_20160609_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='memberimport',
            name='success',
        ),
        migrations.AddField(
            model_name='memberimport',
            name='status',
            field=models.SmallIntegerField(null=True, choices=[(0, 'invalid'), (1, 'saved'), (2, 'unsaved'), (3, 'exception')]),
        ),
        migrations.AlterField(
            model_name='memberimport',
            name='input',
            field=models.FileField(validators=[memberships.validators.member_import_csv_validator], upload_to='memberships/imports/'),
        ),
        migrations.AlterField(
            model_name='memberimport',
            name='output',
            field=models.FileField(null=True, blank=True, upload_to='memberships/imports/'),
        ),
    ]
