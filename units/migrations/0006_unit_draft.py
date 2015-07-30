# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0005_auto_20150123_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='draft',
            field=models.BooleanField(help_text='Drafts are not shown on the main units page', default=False),
            preserve_default=False,
        ),
    ]
