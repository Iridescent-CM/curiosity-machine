# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='description',
            field=models.TextField(null=True, help_text='blurb for the unit', blank=True),
            preserve_default=True,
        ),
    ]
