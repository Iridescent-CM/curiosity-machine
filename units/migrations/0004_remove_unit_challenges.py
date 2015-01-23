# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0003_resource'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unit',
            name='challenges',
        ),
    ]
