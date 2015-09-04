# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0006_unit_draft'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='draft',
            field=models.BooleanField(default=True, help_text='Drafts are not shown on the main units page'),
        ),
    ]
