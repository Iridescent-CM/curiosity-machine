# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0002_resource'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.TextField(help_text='name of the resource'),
        ),
    ]
