# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import memberships.validators
import memberships.models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0011_auto_20160614_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberimport',
            name='input',
            field=models.FileField(validators=[memberships.validators.member_import_csv_validator], help_text='Input file must be csv format, utf-8 encoding', upload_to=memberships.models.member_import_path),
        ),
        migrations.AlterField(
            model_name='memberimport',
            name='output',
            field=models.FileField(null=True, blank=True, upload_to=memberships.models.member_import_path),
        ),
        migrations.AlterField(
            model_name='memberimport',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'invalid'), (1, 'saved'), (2, 'unsaved'), (3, 'exception')], null=True, blank=True),
        ),
    ]
