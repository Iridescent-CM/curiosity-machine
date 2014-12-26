# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '__first__'),
        ('units', '0003_unit_overview'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='standards_alignment_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image', to_field='id', blank=True),
            preserve_default=True,
        ),
    ]
