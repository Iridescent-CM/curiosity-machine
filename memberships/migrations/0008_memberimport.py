# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import memberships.models
import memberships.validators


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0007_auto_20160526_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberImport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('input', models.FileField(upload_to=memberships.models.member_import_path, help_text='Input file must be csv format, utf-8 encoding', validators=[memberships.validators.member_import_csv_validator])),
                ('output', models.FileField(blank=True, null=True, upload_to=memberships.models.member_import_path)),
                ('status', models.SmallIntegerField(choices=[(0, 'invalid'), (1, 'saved'), (2, 'unsaved'), (3, 'exception')], null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('membership', models.ForeignKey(to='memberships.Membership')),
            ],
        ),
    ]
