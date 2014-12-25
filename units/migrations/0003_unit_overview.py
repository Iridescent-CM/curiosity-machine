# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0002_unit_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='overview',
            field=models.TextField(blank=True, null=True, help_text='overview for the unit'),
            preserve_default=True,
        ),
    ]
